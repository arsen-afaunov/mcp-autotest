from browser.bridge import BrowserBridge
from browser.page import Page
from config import WS_HOST, WS_PORT
from transport.websocket import WebSocketTransport


class BrowserClient:
    def __init__(self) -> None:
        self._transport = WebSocketTransport(WS_HOST, WS_PORT)
        self._bridge = BrowserBridge(self._transport)
        self._page = Page(self._bridge)

    async def start(self) -> None:
        await self._transport.start()

    async def stop(self) -> None:
        await self._transport.stop()

    def get_page(self) -> Page:
        return self._page
