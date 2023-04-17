import logging
import os
from configparser import ConfigParser
from enum import Enum
from pathlib import Path
from typing import List, Literal, Optional, Union

import requests
from pydantic import BaseModel, FilePath, HttpUrl

from atlant.auth import (
    LOCALLY_MANAGED_CLIENT_AUDIENCE,
    APIKeyAuthenticator,
    AuthenticatorBase,
    DummyAuthenticator,
    OAuthClientCredentialsAuthenticator,
    Scope,
)

CONFIG_FILE_NAME = "atlant.ini"
PACKAGE_NAME = "atlant"


class OAuthConfig(BaseModel):
    type: Literal["oauth"]
    client_id: str
    client_secret: str
    audience: str = LOCALLY_MANAGED_CLIENT_AUDIENCE
    authorization_url: HttpUrl


class APIKeyConfig(BaseModel):
    type: Literal["api-key"]
    api_key: str


class LogLevel(Enum):
    CRITICAL = "critical"
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"
    DEBUG = "debug"

    def to_numeric_level(self) -> int:
        return {
            LogLevel.CRITICAL: logging.CRITICAL,
            LogLevel.ERROR: logging.ERROR,
            LogLevel.WARNING: logging.WARNING,
            LogLevel.INFO: logging.INFO,
            LogLevel.DEBUG: logging.DEBUG,
        }[self]


class Config(BaseModel):
    scanning_url: HttpUrl
    management_url: Optional[HttpUrl] = None
    authentication: Union[OAuthConfig, APIKeyConfig, None] = None
    certificate_path: Optional[FilePath] = None
    log_level: Optional[LogLevel] = None

    def get_authenticator(
        self,
        session: requests.Session,
        scopes: List[Scope],
    ) -> AuthenticatorBase:
        if isinstance(self.authentication, OAuthConfig):
            return OAuthClientCredentialsAuthenticator(
                session,
                self.authentication.authorization_url,
                self.authentication.client_id,
                self.authentication.client_secret,
                self.authentication.audience,
                scopes,
            )
        elif isinstance(self.authentication, APIKeyConfig):
            return APIKeyAuthenticator(self.authentication.api_key)
        elif self.authentication is None:
            return DummyAuthenticator()
        assert False


def find_config_file(package_name: str, config_file: str) -> Optional[Path]:
    home = Path.home()
    path = home / f".{config_file}"
    if path.is_file():
        return path
    xdg_config_home = Path(os.environ.get("XDG_CONFIG_HOME", home / ".config"))
    path = xdg_config_home / package_name / config_file
    if path.is_file():
        return path
    xdg_config_dirs = os.environ.get("XDG_CONFIG_DIRS")
    if xdg_config_dirs is not None:
        for dir in xdg_config_dirs.split(":"):
            path = Path(dir) / package_name / config_file
            if path.is_file():
                return path
    path = Path("/etc/xdg") / package_name / config_file
    if path.is_file():
        return path
    return None


def read_config_file(path: Optional[Path]) -> Config:
    if path is not None:
        contents = path.read_text()
    else:
        config_path = find_config_file(PACKAGE_NAME, CONFIG_FILE_NAME)
        if config_path is None:
            raise Exception("No configuration file available.")
        contents = config_path.read_text()
    config_parser = ConfigParser(interpolation=None)
    config_parser.read_string(contents)
    raw_config = {
        section_name: {key: value for key, value in section_contents.items()}
        for section_name, section_contents in config_parser.items()
    }
    main_section = raw_config.pop("atlant")
    return Config(**main_section, **raw_config)
