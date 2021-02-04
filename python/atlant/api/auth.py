from dataclasses import dataclass

import requests

from .common import APIException

DEFAULT_SCOPES = ("scan", "management")


@dataclass
class Token:
    token: str
    expires: int


class AuthClient:
    def __init__(self, address, client_id, client_secret):
        self.address = address
        self.client_id = client_id
        self.client_secret = client_secret

    def fetch_token(self, scopes=DEFAULT_SCOPES):
        response = requests.post(
            "https://{}/api/token/v1".format(self.address),
            {
                "grant_type": "client_credentials",
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "audience": "f-secure-atlant",
                "scope": " ".join(scopes),
            },
        )
        data = response.json()
        if response.status_code == 200:
            return Token(token=data["access_token"], expires=data["expires_in"])
        raise APIException(
            data.get("error"),
            data.get("error_description", "Unknown authentication error"),
        )


class AuthenticatedClientBase:
    def __init__(self, authenticator, scopes):
        self._authenticator = authenticator
        self._scopes = scopes
        self._token = None

    def _request(self, method, url, **kwargs):
        if self._token is None:
            self._refresh_token()
        for _ in range(2):
            headers = {
                **kwargs.get("headers", {}),
                "Authorization": "Bearer {}".format(self._token.token),
            }
            kwargs = {**kwargs, "headers": headers}
            response = requests.request(method, url, **kwargs)
            if response.status_code == 401:
                self._refresh_token()
            else:
                break
        return response

    def _refresh_token(self):
        self._token = self._authenticator.fetch_token(self._scopes)
