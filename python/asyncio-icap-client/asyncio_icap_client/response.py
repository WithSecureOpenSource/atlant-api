from dataclasses import dataclass
from typing import Dict, Optional

ResponseBody = Optional[bytes]


@dataclass
class ICAPResponse:
    status: int
    reason: str
    headers: Dict[str, str]

    encapsulated_request_headers: Optional[bytes] = None
    encapsulated_response_headers: Optional[bytes] = None

    encapsulated_request_body: ResponseBody = None
    encapsulated_response_body: ResponseBody = None
    options_body: ResponseBody = None
