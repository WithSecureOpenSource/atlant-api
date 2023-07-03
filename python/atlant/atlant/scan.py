import logging
import time
import urllib.parse
from enum import Enum
from functools import cached_property
from typing import BinaryIO, List, Optional, Tuple, Union

import requests
from pydantic import BaseModel

from .auth import AuthenticatorBase
from .common import APIException


class ScanStatus(Enum):
    PENDING = "pending"
    COMPLETE = "complete"


class ScanResult(Enum):
    CLEAN = "clean"
    WHITELISTED = "whitelisted"
    SUSPICIOUS = "suspicious"
    PUA = "PUA"
    UA = "UA"
    HARMFUL = "harmful"

    @property
    def is_safe(self) -> bool:
        return self in {ScanResult.CLEAN, ScanResult.WHITELISTED}


class DetectionCategory(Enum):
    SUSPICIOUS = "suspicious"
    PUA = "PUA"
    UA = "UA"
    HARMFUL = "harmful"


class Detection(BaseModel):
    category: DetectionCategory
    name: str
    member_name: Optional[str]


class ScanWarnings(BaseModel):
    corrupted: bool = False
    encrypted: bool = False
    max_nested: bool = False
    max_results: bool = False
    max_scan_time: bool = False
    need_content: bool = False

    @property
    def any(self) -> bool:
        """True if any warnings were set."""

        return (
            self.corrupted
            or self.encrypted
            or self.max_nested
            or self.max_results
            or self.max_scan_time
            or self.need_content
        )


class PollSettings(BaseModel):
    poll_path: str
    retry_after: int


class ScanResponse(BaseModel):
    status: ScanStatus
    scan_result: ScanResult
    detections: List[Detection]
    uri_categories: Optional[List[str]] = None
    warnings: ScanWarnings

    poll_settings: Optional[PollSettings] = None


class SecurityCloudSettings(BaseModel):
    allow_upstream_application_files: Optional[bool] = None
    allow_upstream_data_files: Optional[bool] = None


class ScanSettings(BaseModel):
    scan_archives: Optional[bool] = None
    max_nested: Optional[int] = None
    max_scan_time: Optional[int] = None
    stop_on_first: Optional[bool] = None
    allow_upstream_metadata: Optional[bool] = None
    antispam: Optional[bool] = None
    scan_embedded_urls: Optional[bool] = None
    forbidden_uri_categories: Optional[List[str]] = None
    security_cloud: Optional[SecurityCloudSettings] = None


class ScanContentMetadata(BaseModel):
    sha1: Optional[str] = None
    uri: Optional[str] = None
    content_length: Optional[int] = None
    content_type: Optional[str] = None
    charset: Optional[str] = None
    ip: Optional[str] = None
    sender: Optional[str] = None
    recipients: Optional[List[str]] = None


class ScanMetadata(BaseModel):
    scan_settings: Optional[ScanSettings] = None
    content_meta: Optional[ScanContentMetadata] = None


class ScanClient:
    def __init__(
        self,
        session: requests.Session,
        service_url: str,
        authenticator: AuthenticatorBase,
    ):
        self.session = session
        self.service_url = service_url
        self.authenticator = authenticator

    @cached_property
    def scan_url(self) -> str:
        return urllib.parse.urljoin(self.service_url, "api/scan/v1")

    def scan(
        self,
        metadata: ScanMetadata,
        file: Optional[BinaryIO] = None,
    ) -> ScanResponse:
        """Perform a scan"""
        FormData = List[Tuple[str, Tuple[Optional[str], Union[str, BinaryIO], str]]]
        form_data: FormData = [
            ("metadata", (None, metadata.json(), "application/json")),
        ]
        if file is not None:
            form_data.append(
                ("data", (None, file, "application/octet-stream")),
            )
        request = requests.Request("POST", self.scan_url, files=form_data)
        response = self.authenticator.perform_request(self.session, request)
        if response.status_code == 200:
            return ScanResponse(**response.json())
        elif response.status_code == 202:
            # If status code is 202 the scan is not complete and client should poll for updates
            poll_path = response.headers["Location"]
            retry_after = int(response.headers["Retry-After"])
            poll_settings = PollSettings(
                poll_path=poll_path,
                retry_after=retry_after,
            )
            return ScanResponse(
                **response.json(),
                poll_settings=poll_settings,
            )
        else:
            raise APIException(
                "Scan error",
                f"Received unexpected response status {response.status_code}",
            )

    def url_for_poll_path(self, poll_path: str) -> str:
        return urllib.parse.urljoin(self.service_url, poll_path)

    def poll(self, poll_path: str) -> ScanResponse:
        """Poll a pending scan task"""
        request = requests.Request("GET", self.url_for_poll_path(poll_path))
        response = self.authenticator.perform_request(self.session, request)
        if response.status_code == 200:
            return ScanResponse(**response.json())
        raise APIException(
            "Scan error",
            f"Received unexpected response status {response.status_code}",
        )

    def scan_until_completion(
        self,
        metadata: ScanMetadata,
        file: Optional[BinaryIO] = None,
    ) -> ScanResponse:
        """Perform a scan and poll until the scan is fully completed"""
        response = self.scan(metadata, file)
        if response.status == ScanStatus.COMPLETE:
            return response
        elif response.status == ScanStatus.PENDING:
            while True:
                assert response.poll_settings is not None
                logging.debug(
                    f"Scan was not fully completed, sleeping for {response.poll_settings.retry_after} seconds",
                )
                time.sleep(response.poll_settings.retry_after)
                response = self.poll(response.poll_settings.poll_path)
                if response.status == ScanStatus.COMPLETE:
                    return response
                elif response.status == ScanStatus.PENDING:
                    continue
        else:
            assert False
