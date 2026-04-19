import asyncio
import json
import uuid
from collections.abc import Callable, Awaitable

from pydantic import BaseModel

from protocol import CommandResponse, Message
from transport import Transport


class BrowserBridge:
    def __init__(self, transport: Transport) -> None:
        self._transport = transport
        self._pending: dict[str, asyncio.Future[CommandResponse]] = {}
        transport.on_message(self._on_message)
        transport.on_disconnect(self._on_disconnect)

    async def send_command(self, body: BaseModel, timeout: float = 30.0) -> CommandResponse:
        request_id = uuid.uuid4().hex
        msg = Message(id=request_id, body=body)
        raw = msg.model_dump_json()

        future = asyncio.get_event_loop().create_future()
        self._pending[request_id] = future

        await self._transport.send(raw)

        try:
            return await asyncio.wait_for(future, timeout=timeout)
        except asyncio.TimeoutError:
            self._pending.pop(request_id, None)
            raise

    async def _on_message(self, raw: str) -> None:
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            return

        try:
            response = CommandResponse.model_validate(data)
        except Exception:
            return

        request_id = response.id
        if request_id in self._pending:
            self._pending.pop(request_id).set_result(response)

    def _on_disconnect(self) -> None:
        for request_id, future in list(self._pending.items()):
            if not future.done():
                future.set_exception(ConnectionError("Transport disconnected"))
        self._pending.clear()
