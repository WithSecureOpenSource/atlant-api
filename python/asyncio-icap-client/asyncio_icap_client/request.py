from dataclasses import dataclass
from enum import Enum
from typing import Dict, Optional, Union

from .async_readable import AsyncReadable


class RequestMethod(Enum):
    REQMOD = "REQMOD"
    RESPMOD = "RESPMOD"
    OPTIONS = "OPTIONS"


RequestBody = Union[bytes, AsyncReadable, None]


@dataclass
class ICAPRequest:
    method: RequestMethod
    path: Optional[str]
    params: Dict[str, str]
    headers: Dict[str, str]

    encapsulated_request_headers: Optional[bytes] = None
    encapsulated_response_headers: Optional[bytes] = None

    encapsulated_request_body: RequestBody = None
    encapsulated_response_body: RequestBody = None
    options_body: RequestBody = None

    def __post_init__(self) -> None:
        bodies = sum(
            (
                self.encapsulated_request_body is not None,
                self.encapsulated_response_body is not None,
                self.options_body is not None,
            )
        )
        if bodies > 1:
            raise ValueError(
                "ICAP requests can contain at most one body.",
            )
