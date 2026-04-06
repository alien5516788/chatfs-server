import json

from fastapi import APIRouter

from src.clientmanager import clientManager

router = APIRouter(prefix="/{clientId}")


@router.get("/")
async def hello(clientId: str):
    client = await clientManager.get_client(clientId)

    if client:
        return json.dumps({"status": True, "message": "Client exists"})

    else:
        return json.dumps({"status": False, "message": "Client does not exists"})
