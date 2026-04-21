# Request/response format follows protocol/ JSON Schema:
#   Envelope { id, body } wraps commands and responses.
#   Extension must be updated to match this format (see active issues).

from browser.bridge import BrowserBridge
from protocol.domain.click_command import ClickCommand, Args as ClickCommandArgs
from protocol.domain.run_command import RunCommand, Args as RunCommandArgs
from protocol.domain.command_response import CommandResponse


class Page:
    def __init__(self, bridge: BrowserBridge) -> None:
        self._bridge = bridge

    async def click(self, selector: str) -> CommandResponse:
        command = ClickCommand(args=ClickCommandArgs(selector=selector))
        response = await self._bridge.send_command(command.model_dump())
        return CommandResponse.model_validate(response)

    async def run(self, code: str) -> CommandResponse:
        command = RunCommand(args=RunCommandArgs(code=code))
        response = await self._bridge.send_command(command.model_dump())
        return CommandResponse.model_validate(response)
