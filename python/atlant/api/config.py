import urllib.parse

from .auth import AuthenticatedClientBase
from .common import APIException


class ConfigClient(AuthenticatedClientBase):
    def __init__(self, address, authenticator):
        super().__init__(authenticator, ["management"])
        self.address = address

    def get(self, setting):
        response = self._request(
            "GET",
            "https://{}/api/atlant/config/v1/{}".format(
                self.address,
                "/".join(urllib.parse.quote(p, safe="") for p in setting),
            ),
        )
        data = response.json()
        if response.status_code == 200:
            return data
        raise APIException(data["title"], data["message"])

    def set(self, setting, value):
        response = self._request(
            "PUT",
            "https://{}/api/atlant/config/v1/{}".format(
                self.address,
                "/".join(urllib.parse.quote(p, safe="") for p in setting),
            ),
            json=value,
        )
        if response.status_code != 200:
            data = response.json()
            raise APIException(data["title"], data["message"])
