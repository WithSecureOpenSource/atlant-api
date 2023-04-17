from typing import Protocol, runtime_checkable


@runtime_checkable
class AsyncReadable(Protocol):
    async def read(self, amount: int) -> bytes:
        ...
