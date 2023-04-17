import asyncio
from types import TracebackType
from typing import Dict, Optional, Type

from .connection import ICAPConnection

DEFAULT_ICAP_PORT = 1344


class ICAPClient:
    def __init__(
        self,
        host: str,
        port: int = DEFAULT_ICAP_PORT,
        *,
        headers: Optional[Dict[str, str]] = None,
    ):
        self.host = host
        self.port = port
        self.headers = headers
        self._connection: Optional[ICAPConnection] = None

    async def connect(self) -> ICAPConnection:
        assert self._connection is None
        reader, writer = await asyncio.open_connection(self.host, self.port)
        self._connection = ICAPConnection(
            self.host,
            self.port,
            reader,
            writer,
            headers=self.headers,
        )
        return self._connection

    async def close(self) -> None:
        assert self._connection is not None
        await self._connection.close()
        self._connection = None

    async def __aenter__(self) -> ICAPConnection:
        await self.connect()
        assert self._connection is not None
        return self._connection

    async def __aexit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_value: Optional[BaseException],
        traceback: Optional[TracebackType],
    ) -> None:
        if self._connection is not None:
            await self.close()
