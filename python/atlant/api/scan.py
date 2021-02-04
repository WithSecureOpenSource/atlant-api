import json
import time
import logging
from dataclasses import dataclass
from typing import List, Optional
from enum import Enum, auto

from .auth import AuthenticatedClientBase
from .common import APIException


class ScanStatus(Enum):
    PENDING = auto()
    COMPLETE = auto()

    @classmethod
    def from_str(cls, value):
        status = {
            "pending": cls.PENDING,
            "complete": cls.COMPLETE,
        }.get(value)
        if status is None:
            raise ValueError("Unknown scan status {!r}".format(value))
        return status


class ScanResult(Enum):
    CLEAN = auto()
    WHITELISTED = auto()
    SUSPICIOUS = auto()
    PUA = auto()
    UA = auto()
    HARMFUL = auto()

    @property
    def is_safe(self):
        return self in (self.CLEAN, self.WHITELISTED)

    @classmethod
    def from_str(cls, value):
        result = {
            "clean": cls.CLEAN,
            "whitelisted": cls.WHITELISTED,
            "suspicious": cls.SUSPICIOUS,
            "PUA": cls.PUA,
            "UA": cls.UA,
            "harmful": cls.HARMFUL,
        }.get(value)
        if result is None:
            raise ValueError("Unknown scan result {!r}".format(value))
        return result


class DetectionCategory(Enum):
    SUSPICIOUS = auto()
    PUA = auto()
    UA = auto()
    HARMFUL = auto()

    @classmethod
    def from_str(cls, value):
        result = {
            "suspicious": cls.SUSPICIOUS,
            "PUA": cls.PUA,
            "UA": cls.UA,
            "harmful": cls.HARMFUL,
        }.get(value)
        if result is None:
            raise ValueError("Unknown detection category {!r}".format(value))
        return result


@dataclass
class Detection:
    category: DetectionCategory
    name: str
    member_name: Optional[str]


@dataclass
class ScanResponse:
    status: ScanStatus
    result: ScanResult
    detections: List[Detection]
    task_url: Optional[str]
    retry_after: Optional[int]


class ScanClient(AuthenticatedClientBase):
    def __init__(self, address, authenticator):
        super().__init__(authenticator, ["scan"])
        self.address = address

    def scan(self, file_obj=None, metadata=None):
        """Scan a file"""
        assert file_obj is not None or metadata is not None
        if metadata is None:
            metadata = {}
        request_parts = [
            ("metadata", (None, json.dumps(metadata))),
        ]
        if file_obj is not None:
            request_parts.append(
                ("data", (None, file_obj)),
            )
        response = self._request(
            "POST",
            "https://{}/api/scan/v1".format(self.address),
            files=request_parts,
        )
        if response.status_code in (200, 202):
            return _make_scan_response(response)
        print(response)
        raise APIException(
            "Scan error",
            "Scan failed (status {})".format(response.status_code),
        )

    def poll(self, task_url):
        """Poll a pending scan task"""
        response = self._request(
            "GET",
            "https://{}{}".format(self.address, task_url),
        )
        if response.status_code == 200:
            return _make_scan_response(response)
        raise APIException(
            "Scan error",
            "Unknown response from scan API (status {})".format(response.status_code),
        )

    def scan_until_complete(self, file_obj=None, metadata=None):
        """Scan a file and poll until the scan is completed"""
        assert file_obj is not None or metadata is not None
        response = self.scan(file_obj, metadata)
        if response.status == ScanStatus.COMPLETE:
            return response
        elif response.status == ScanStatus.PENDING:
            task_url = response.task_url
            logging.debug("Scanner returned pending status. Waiting %d seconds", response.retry_after)
            time.sleep(response.retry_after)
            while True:
                response = self.poll(task_url)
                if response.status == ScanStatus.COMPLETE:
                    return response
                elif response.status == ScanStatus.PENDING:
                    logging.debug("Scanner returned pending status. Waiting %d seconds", response.retry_after)
                    time.sleep(response.retry_after)
                    continue
                else:
                    break
            raise APIException(
                "Scan error",
                "Unknown response from scan API (status {})".format(
                    response.status
                ),
            )


def _make_scan_response(response):
    task_url = response.headers.get("Location")
    retry_after = response.headers.get("Retry-After")
    if retry_after is not None:
        retry_after = int(retry_after)
    data = response.json()
    return ScanResponse(
        status=ScanStatus.from_str(data["status"]),
        result=ScanResult.from_str(data["scan_result"]),
        detections=[
            Detection(
                category=DetectionCategory.from_str(detection["category"]),
                name=detection["name"],
                member_name=detection.get("member_name"),
            )
            for detection in data.get("detections", [])
        ],
        task_url=task_url,
        retry_after=retry_after,
    )
