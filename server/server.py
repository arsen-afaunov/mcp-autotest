import asyncio
import json
import os
from pathlib import Path

import websockets
from dotenv import load_dotenv

env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

WS_HOST = os.getenv("WS_HOST", "localhost")
WS_PORT = int(os.getenv("WS_PORT", "8765"))

# TODO: consider more sophisticated client routing (multi-client registry, clientId, etc.)
#
# TODO: MCP skill delivery strategy
#   - MCP protocol does not support "push" system instructions from server to LLM
#   - Options: (1) detailed tool descriptions, (2) dedicated get_instructions() tool,
#     (3) get_testing_strategy() short cheat-sheet, (4) client-side config (.cursorrules)
#   - Performance: calling get_instructions() on every action has token overhead
#     (~2000-4000 tokens per call). Recommended hybrid: inline hints in tool descriptions
#     + get_testing_strategy() for concise strategy + get_full_guide() called once
#
# TODO: add MCP tools for LLM-driven testing workflow:
#   - get_testing_strategy() - returns concise testing strategy (300-500 tokens)
#   - get_full_guide() - returns full testing & Playwright guide (called once)
#   - Future: get_dom(), get_url(), screenshot() for state verification
ext_ws = None


async def handler(websocket):
    global ext_ws
    try:
        async for message in websocket:
            data = json.loads(message)
            print(f"[Server] Received: {data}")

            if data.get("type") == "register":
                ext_ws = websocket
                print("[Server] Extension registered")
                continue

            if ext_ws is not None:
                try:
                    await ext_ws.send(message)
                except websockets.ConnectionClosed:
                    ext_ws = None
                    print("[Server] Extension disconnected during send")
                except Exception as e:
                    print(f"[Server] Unexpected send error: {type(e).__name__}: {e}")
                    ext_ws = None
    finally:
        if ext_ws is websocket:
            ext_ws = None


async def main():
    async with websockets.serve(handler, WS_HOST, WS_PORT):
        print(f"[Server] WebSocket server started on ws://{WS_HOST}:{WS_PORT}")
        await asyncio.Future()


if __name__ == "__main__":
    asyncio.run(main())
