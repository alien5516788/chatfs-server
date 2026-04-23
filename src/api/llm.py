import re

from fastapi import APIRouter, Depends, Request

from src.socket import client_manager
from src.socket.client import Client
from src.types import LLMResponse

router = APIRouter(prefix="/{clientId}")


@router.get("/")
async def llm(client: Client = Depends(client_manager.get_client)) -> LLMResponse:
    if not client:
        return LLMResponse(status=False, result="Expired or invalid client ID")

    return LLMResponse(status=True, result=f"Client '{client.client_id}' is online")


@router.get("/{command}")
async def command(
    request: Request, command: str, client: Client = Depends(client_manager.get_client)
) -> LLMResponse:
    if not client:
        return LLMResponse(status=False, result="Expired or invalid client ID")

    if not re.match(r"^[a-z][a-z_]*$", command):
        return LLMResponse(
            status=False, result="Command must only consist of lowercase letters"
        )

    params = dict(request.query_params)

    return await client.send_llm_command(command, params)
