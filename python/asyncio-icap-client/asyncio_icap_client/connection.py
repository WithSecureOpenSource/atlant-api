import asyncio
from typing import Dict, Optional

from ._decoder import ICAPResponseDecoder, Incomplete
from ._encoder import ICAPRequestEncoder
from .errors import ICAPProtocolError
from .request import ICAPRequest, RequestBody, RequestMethod
from .response import ICAPResponse


class ICAPConnection:
    def __init__(
        self,
        host: str,
        port: int,
        reader: asyncio.StreamReader,
        writer: asyncio.StreamWriter,
        *,
        headers: Optional[Dict[str, str]] = None,
    ):
        self._reader = reader
        self._writer = writer
        self._headers = headers
        self._decoder = ICAPResponseDecoder()
        self._encoder = ICAPRequestEncoder(host, port, self._writer)
        self._request_lock = asyncio.Lock()

    def _prepare_request(self, request: ICAPRequest) -> ICAPRequest:
        if self._headers is None:
            return request
        headers = dict(self._headers)
        headers.update(request.headers)
        return ICAPRequest(
            method=request.method,
            path=request.path,
            params=request.params,
            headers=headers,
            encapsulated_request_headers=request.encapsulated_request_headers,
            encapsulated_response_headers=request.encapsulated_response_headers,
            encapsulated_request_body=request.encapsulated_request_body,
            encapsulated_response_body=request.encapsulated_response_body,
            options_body=request.options_body,
        )

    async def request(self, request: ICAPRequest) -> ICAPResponse:
        chunk_size = 4096
        request = self._prepare_request(request)
        async with self._request_lock:
            await self._encoder.send_request(request)
            while True:
                data = await self._reader.read(chunk_size)
                if not data:
                    raise ICAPProtocolError()
                self._decoder.feed(data)
                response = self._decoder.decode_response()
                if not isinstance(response, Incomplete):
                    return response

    async def reqmod(
        self,
        path: Optional[str] = None,
        params: Optional[Dict[str, str]] = None,
        headers: Optional[Dict[str, str]] = None,
        encapsulated_request_headers: Optional[bytes] = None,
        encapsulated_request_body: RequestBody = None,
    ) -> ICAPResponse:
        request = ICAPRequest(
            method=RequestMethod.REQMOD,
            path=path,
            params=params if params is not None else {},
            headers=headers if headers is not None else {},
            encapsulated_request_headers=encapsulated_request_headers,
            encapsulated_request_body=encapsulated_request_body,
        )
        return await self.request(request)

    async def respmod(
        self,
        path: Optional[str] = None,
        params: Optional[Dict[str, str]] = None,
        headers: Optional[Dict[str, str]] = None,
        encapsulated_request_headers: Optional[bytes] = None,
        encapsulated_response_headers: Optional[bytes] = None,
        encapsulated_response_body: RequestBody = None,
    ) -> ICAPResponse:
        request = ICAPRequest(
            method=RequestMethod.RESPMOD,
            path=path,
            params=params if params is not None else {},
            headers=headers if headers is not None else {},
            encapsulated_request_headers=encapsulated_request_headers,
            encapsulated_response_headers=encapsulated_response_headers,
            encapsulated_response_body=encapsulated_response_body,
        )
        return await self.request(request)

    async def options(
        self,
        path: Optional[str] = None,
        params: Optional[Dict[str, str]] = None,
        headers: Optional[Dict[str, str]] = None,
        options_body: RequestBody = None,
    ) -> ICAPResponse:
        request = ICAPRequest(
            method=RequestMethod.OPTIONS,
            path=path,
            params=params if params is not None else {},
            headers=headers if headers is not None else {},
            options_body=options_body,
        )
        return await self.request(request)

    async def close(self) -> None:
        self._writer.close()
        await self._writer.wait_closed()
