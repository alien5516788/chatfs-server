import json

from fastapi import APIRouter, Depends

from src.api.llm_ops.list import router as list_router
from src.clientmanager import clientManager

router = APIRouter(prefix="/{clientId}")

router.include_router(list_router)


@router.get("/")
async def hello(client=Depends(clientManager.get_client)):
    if not client:
        return json.dumps({"status": False, "message": "Invalid client ID"})

    return json.dumps({"status": True, "message": f"Client '{client.clientId}' found"})
