import logging
import urllib.parse
from abc import ABC, abstractmethod
from enum import Enum
from functools import cached_property
from typing import Iterable, Optional

import requests
from pydantic import BaseModel

from .common import APIException


class Scope(Enum):
    SCAN = "scan"
    MANAGEMENT = "management"


DEFAULT_SCOPES = frozenset({Scope.SCAN, Scope.MANAGEMENT})

# Audience to be used with clients that have been created locally using atlantctl
# command.
LOCALLY_MANAGED_CLIENT_AUDIENCE = "f-secure-atlant"

# Audience to be used with clients that have been created with Policy Manager
# Console.
POLICY_MANAGER_MANAGED_CLIENT_AUDIENCE = "policy-manager"


class OAuthAccessToken(BaseModel):
    access_token: str
    expires_in: int


class OAuthErrorResponse(BaseModel):
    error: str
    error_description: str

    def to_exception(self) -> APIException:
        return APIException(self.error, self.error_description)


class OAuthClientCredentialsClient:
    def __init__(self, session: requests.Session, service_url: str) -> None:
        self.session = session
        self.service_url = service_url

    def get_access_token(
        self,
        client_id: str,
        client_secret: str,
        audience: str = LOCALLY_MANAGED_CLIENT_AUDIENCE,
        scopes: Iterable[Scope] = DEFAULT_SCOPES,
    ) -> OAuthAccessToken:
        logging.debug("Getting access token.")
        response = self.session.post(
            self.token_url,
            {
                "grant_type": "client_credentials",
                "client_id": client_id,
                "client_secret": client_secret,
                "audience": audience,
                "scope": " ".join(scope.value for scope in scopes),
            },
        )
        data = response.json()
        if response.status_code == 200:
            return OAuthAccessToken(**data)
        raise OAuthErrorResponse(**data).to_exception()

    @cached_property
    def token_url(self) -> str:
        return urllib.parse.urljoin(self.service_url, "api/token/v1")


class AuthenticatorBase(ABC):
    @abstractmethod
    def perform_request(
        self,
        session: requests.Session,
        request: requests.Request,
    ) -> requests.Response:
        """Perform authenticated request"""


class OAuthClientCredentialsAuthenticator(AuthenticatorBase):
    def __init__(
        self,
        # Session to use for making authentication requests
        session: requests.Session,
        # Authentication service URL
        service_url: str,
        # Client ID
        client_id: str,
        # Client secret
        client_secret: str,
        # Client audience
        audience: str = LOCALLY_MANAGED_CLIENT_AUDIENCE,
        # Scopes for access tokens
        scopes: Iterable[Scope] = DEFAULT_SCOPES,
    ):
        self.client = OAuthClientCredentialsClient(session, service_url)
        self.client_id = client_id
        self.client_secret = client_secret
        self.audience = audience
        self.scopes = frozenset(scopes)
        self.token: Optional[OAuthAccessToken] = None

    def perform_request(
        self,
        session: requests.Session,
        request: requests.Request,
    ) -> requests.Response:
        if self.token is None:
            self.token = self.client.get_access_token(
                self.client_id,
                self.client_secret,
                self.audience,
                self.scopes,
            )
        response = self._send_request(session, request)
        if response.status_code != 401:
            return response
        logging.debug("Received unauthorized response, refreshing access token.")
        self.token = self.client.get_access_token(
            self.client_id,
            self.client_secret,
            self.audience,
            self.scopes,
        )
        response = self._send_request(session, request)
        if response.status_code == 401:
            raise APIException(
                "Authentication failed",
                "Performing authenticated request failed",
            )
        return response

    def _send_request(
        self,
        session: requests.Session,
        request: requests.Request,
    ) -> requests.Response:
        assert self.token is not None
        request.headers["Authorization"] = f"Bearer {self.token.access_token}"
        prepared_request = session.prepare_request(request)
        return session.send(prepared_request)


class APIKeyAuthenticator(AuthenticatorBase):
    def __init__(self, api_key: str):
        self.api_key = api_key

    def perform_request(
        self,
        session: requests.Session,
        request: requests.Request,
    ) -> requests.Response:
        request.headers["X-Api-Key"] = self.api_key
        prepared_request = session.prepare_request(request)
        return session.send(prepared_request)


class DummyAuthenticator(AuthenticatorBase):
    def perform_request(
        self,
        session: requests.Session,
        request: requests.Request,
    ) -> requests.Response:
        prepared_request = session.prepare_request(request)
        return session.send(prepared_request)
