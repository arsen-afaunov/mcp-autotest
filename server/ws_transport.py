import json

import websockets

from transport import Transport


class WebSocketTransport(Transport):
    def __init__(self, host: str, port: int) -> None:
        self._host = host
        self._port = port
        self._server = None
        self._ext_ws = None
        self._on_message_handler = None
        self._on_disconnect_handler = None

    async def start(self) -> None:
        self._server = await websockets.serve(self._handler, self._host, self._port)

    async def stop(self) -> None:
        if self._server:
            self._server.close()
            await self._server.wait_closed()

    async def send(self, raw_message: str) -> None:
        if self._ext_ws is None:
            raise ConnectionError("Extension not connected")
        await self._ext_ws.send(raw_message)

    def on_message(self, handler) -> None:
        self._on_message_handler = handler

    def on_disconnect(self, handler) -> None:
        self._on_disconnect_handler = handler

    async def _handler(self, websocket) -> None:
        self._ext_ws = websocket
        try:
            async for message in websocket:
                # TODO: Move register handshake logic out of transport layer.
                # The transport should be message-agnostic.
                try:
                    data = json.loads(message)
                    if data.get("type") == "register":
                        continue
                except json.JSONDecodeError:
                    pass

                if self._on_message_handler:
                    await self._on_message_handler(message)
        finally:
            self._ext_ws = None
            if self._on_disconnect_handler:
                self._on_disconnect_handler()
