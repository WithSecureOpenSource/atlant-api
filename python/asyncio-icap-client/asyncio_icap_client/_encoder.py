import asyncio
import urllib.parse
from typing import Dict, Optional, Union

from ._constants import ICAP_VERSION, NEWLINE
from ._sections import SectionType
from .async_readable import AsyncReadable
from .request import ICAPRequest, RequestMethod


class ICAPRequestEncoder:
    def __init__(self, host: str, port: int, writer: asyncio.StreamWriter):
        self._host = host
        self._port = port
        self._writer = writer

    async def _send_request_line(
        self,
        method: RequestMethod,
        path: Optional[str],
        params: Dict[str, str],
    ) -> None:
        full_url = urllib.parse.urlunparse(
            (
                "icap",  # protocol
                f"{self._host}:{self._port}",  # netloc
                path if path is not None else "",  # path
                "",  # params
                urllib.parse.urlencode(params),  # query
                "",  # fragment
            )
        )
        self._writer.write(
            b"%b %b %b%b"
            % (
                method.value.encode("ascii"),
                full_url.encode("ascii"),
                ICAP_VERSION,
                NEWLINE,
            )
        )
        await self._writer.drain()

    async def _send_headers(self, headers: Dict[str, str]) -> None:
        for header, value in headers.items():
            self._writer.write(
                b"%b: %b%b"
                % (
                    header.encode("ascii"),
                    value.encode("ascii"),
                    NEWLINE,
                )
            )
        self._writer.write(NEWLINE)
        await self._writer.drain()

    async def _send_data(self, data: bytes) -> None:
        self._writer.write(data)
        await self._writer.drain()

    async def _send_chunk(self, data: bytes) -> None:
        self._writer.write(b"%x%b" % (len(data), NEWLINE))
        self._writer.write(data)
        self._writer.write(NEWLINE)
        await self._writer.drain()

    async def _send_terminating_chunk(self) -> None:
        await self._send_chunk(b"")

    async def _send_file(self, handle: AsyncReadable) -> None:
        chunk_size = 4096
        while True:
            data = await handle.read(chunk_size)
            if not data:
                return
            await self._send_chunk(data)

    async def _send_chunked_section(self, data: Union[bytes, AsyncReadable]) -> None:
        if isinstance(data, bytes):
            await self._send_chunk(data)
        elif isinstance(data, AsyncReadable):
            await self._send_file(data)
        await self._send_terminating_chunk()

    async def send_request(self, request: ICAPRequest) -> None:
        await self._send_request_line(
            request.method,
            request.path,
            request.params,
        )
        headers = dict(request.headers)
        headers["Encapsulated"] = self._make_encapsulated_header(request)
        await self._send_headers(headers)
        if request.encapsulated_request_headers is not None:
            await self._send_data(request.encapsulated_request_headers)
        if request.encapsulated_response_headers is not None:
            await self._send_data(request.encapsulated_response_headers)
        if request.encapsulated_request_body is not None:
            await self._send_chunked_section(request.encapsulated_request_body)
        if request.encapsulated_response_body is not None:
            await self._send_chunked_section(request.encapsulated_response_body)
        if request.options_body is not None:
            await self._send_chunked_section(request.options_body)

    def _make_encapsulated_header(self, request: ICAPRequest) -> str:
        fields = []
        offset = 0
        if request.encapsulated_request_headers is not None:
            fields.append((SectionType.RequestHeaders, offset))
            offset += len(request.encapsulated_request_headers)
        if request.encapsulated_response_headers is not None:
            fields.append((SectionType.ResponseHeaders, offset))
            offset += len(request.encapsulated_response_headers)
        if request.encapsulated_request_body is not None:
            fields.append((SectionType.RequestBody, offset))
        if request.encapsulated_response_body is not None:
            fields.append((SectionType.ResponseBody, offset))
        if request.options_body is not None:
            fields.append((SectionType.OptionsBody, offset))
        if not fields:
            fields.append((SectionType.NullBody, offset))
        return ", ".join(f"{section.value}={offset}" for section, offset in fields)
