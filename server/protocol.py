# TODO: Implement a unified JSON Schema source of truth shared between
# the Chrome extension (TypeScript/Zod) and the Python server to prevent
# drift and manual synchronization of message types.

from enum import StrEnum

from pydantic import BaseModel
from typing import Any


class RequestType(StrEnum):
    CLICK = "click"
    RUN = "run"
    REGISTER = "register"


class ClickCommandArgs(BaseModel):
    selector: str


class ClickCommand(BaseModel):
    type: RequestType = RequestType.CLICK
    args: ClickCommandArgs


class ResponseError(BaseModel):
    code: str
    message: str


# TODO: Consider splitting CommandResponse into Message envelope + response body
# to align with the pattern used for outgoing commands.

class CommandResponse(BaseModel):
    id: str
    ok: bool
    result: dict[str, Any] | None = None
    error: ResponseError | None = None


class Message(BaseModel):
    id: str
    body: BaseModel
