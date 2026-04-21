from collections.abc import Callable, Awaitable
from typing import Protocol


class Transport(Protocol):
    async def start(self) -> None:
        ...

    async def stop(self) -> None:
        ...

    async def send(self, raw_message: str) -> None:
        ...

    def on_message(self, handler: Callable[[str], Awaitable[None] | None]) -> None:
        ...

    def on_disconnect(self, handler: Callable[[], None]) -> None:
        ...
