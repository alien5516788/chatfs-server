from typing import Literal

from pydantic import BaseModel


# Message types
# From gateway to client
class ConnectSyn(BaseModel):
    status: bool
    message_type: Literal["connect_syn"]
    gateway_url: str


class Ping(BaseModel):
    status: bool
    message_type: Literal["ping"]


class LlmCommand(BaseModel):
    status: bool
    message_type: Literal["llm_command"]
    id: str
    command: str
    params: dict[str, str]


# Reply types
# From client to gateway
class ConnectAck(BaseModel):
    status: bool
    reply_type: Literal["connect_ack"]


class Pong(BaseModel):
    status: bool
    reply_type: Literal["pong"]


class LlmResult(BaseModel):
    status: bool
    reply_type: Literal["llm_result"]
    id: str
    result: dict | str


# LLM response types
# From gateway to LLM
class LlmResponse(BaseModel):
    status: bool
    result: dict | str
