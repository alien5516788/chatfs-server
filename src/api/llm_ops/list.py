from fastapi import APIRouter, Depends

from src.clientmanager import clientManager
from src.clientmanager.client import Client

router = APIRouter(prefix="/list")


@router.get("/")
async def list(
    path: str = "",
    recursive: str = "false",
    item_type: str = "all",
    client: Client = Depends(clientManager.get_client),
):
    if not client:
        return {"status": False, "error": "Invalid or expired client Id"}

    if recursive not in {"true", "false"}:
        return {
            "status": False,
            "error": "recursive: Recursion must be 'true' or 'false' (not any boolean)",
        }

    if item_type not in {"folder", "file", "all"}:
        return {
            "status": False,
            "error": "item_type: Item type must be 'folder', 'file' or 'all'",
        }

    return await client.send_query_codebase(
        "list",
        {
            "path": path,
            "recursive": True if recursive == "true" else False,
            "item_type": item_type,
        },
    )
