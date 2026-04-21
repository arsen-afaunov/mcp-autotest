from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from dataclasses import dataclass

from mcp.server.fastmcp import Context, FastMCP

from browser.client import BrowserClient
from browser.page import Page


@dataclass
class AppContext:
    page: Page


@asynccontextmanager
async def lifespan(app: FastMCP) -> AsyncIterator[AppContext]:
    client = BrowserClient()
    await client.start()
    try:
        yield AppContext(page=client.get_page())
    finally:
        await client.stop()


async def main():
    server = FastMCP("mcp-autotest", lifespan=lifespan)

    @server.tool()
    async def click(selector: str, ctx: Context) -> str:
        app_ctx = ctx.request_context.lifespan_context
        response = await app_ctx.page.click(selector)
        if response.ok:
            return f"Clicked {selector}"
        return f"Failed to click {selector}: {response.error.message if response.error else 'unknown error'}"

    @server.tool()
    async def run(code: str, ctx: Context) -> str:
        app_ctx = ctx.request_context.lifespan_context
        response = await app_ctx.page.run(code)
        if response.ok:
            return f"Executed code: {response.result}"
        return f"Failed to execute code: {response.error.message if response.error else 'unknown error'}"

    await server.run_stdio_async()


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
