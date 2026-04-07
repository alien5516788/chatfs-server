import json
from typing import Literal

import regex as re
from fastapi import APIRouter, Depends, Query

from src.clientmanager import clientManager
from src.clientmanager.client import Client

router = APIRouter(prefix="/list")


@router.get("/")
async def hello(
    path: str = Query("", pattern=r"^([^/\\]+(\/[^/\\]+)*)?$"),
    recursive: bool = False,
    itemtype: Literal["folder", "file", "all"] = "all",
    client: Client = Depends(clientManager.get_client),
):
    if not client:
        return json.dumps({"status": False, "message": "Invalid client"})

    return await client.send_get_context(
        "list", {"path": path, "recursive": recursive, "itemtype": itemtype}
    )
