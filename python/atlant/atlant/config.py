import urllib.parse
from typing import Any, Iterable

import requests

from .auth import AuthenticatorBase
from .common import APIException


class ConfigClient:
    def __init__(
        self,
        session: requests.Session,
        service_url: str,
        authenticator: AuthenticatorBase,
    ):
        self.session = session
        self.service_url = service_url
        self.authenticator = authenticator

    def url_for_setting(self, path: Iterable[str]) -> str:
        config_base_url = urllib.parse.urljoin(
            self.service_url, "api/atlant/config/v1/"
        )
        setting_path = "/".join(
            urllib.parse.quote(segment, safe="") for segment in path
        )
        return urllib.parse.urljoin(config_base_url, setting_path)

    def get(self, path: Iterable[str]) -> Any:
        request = requests.Request("GET", self.url_for_setting(path))
        response = self.authenticator.perform_request(self.session, request)
        data = response.json()
        if response.status_code == 200:
            return data
        raise APIException(data["title"], data["message"])

    def set(self, path: Iterable[str], value: Any) -> None:
        request = requests.Request("PUT", self.url_for_setting(path), json=value)
        response = self.authenticator.perform_request(self.session, request)
        if response.status_code != 200:
            data = response.json()
            raise APIException(data["title"], data["message"])
