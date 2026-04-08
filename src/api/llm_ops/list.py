from fastapi import APIRouter, Depends

from src.clientmanager import clientManager
from src.clientmanager.client import Client

router = APIRouter(prefix="/list")


@router.get("/")
async def list(
    path: str = "",
    recursive: str = "false",
    itemtype: str = "file",
    client: Client = Depends(clientManager.get_client),
):
    if not client:
        return {"status": False, "message": "Invalid or expired client Id"}

    if recursive not in {"true", "false"}:
        return {
            "status": False,
            "message": "recursive: Recursion must be 'true' or 'false' (not any boolean)",
        }

    if itemtype not in {"folder", "file", "all"}:
        return {
            "status": False,
            "message": "itemtype: Item type must be 'folder', 'file' or 'all'",
        }

    return await client.send_query_codebase(
        "list",
        {
            "path": path,
            "recursive": True if recursive == "true" else False,
            "item_type": itemtype,
        },
    )
