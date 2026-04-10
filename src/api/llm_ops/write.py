import regex as re
from fastapi import APIRouter, Depends

from src.clientmanager import clientManager
from src.clientmanager.client import Client

router = APIRouter(prefix="/write")


# This endpoint is only used by web browser extension for content writing actions
# TODO: Refactor after implementing the extension
@router.post("/")
async def write(
    path: str = "",
    lines: str = "",
    mode: str = "shift",
    content: str = "",
    client: Client = Depends(clientManager.get_client),
):
    if not client:
        return {"status": False, "message": "Invalid or expired client Id"}

    if len(path) <= 0:
        return {
            "status": False,
            "message": "path: File name cannot be empty (e.g. 'path=src/file.txt')",
        }

    if not re.match(r"^(\d+|\*)-(\d+|\*)$", lines):
        return {
            "status": False,
            "message": "lines: Lines must follow the pattern '^(\\d+|\\*)-(\\d+|\\*)$' (e.g. 'lines=1-*', 'lines=3-6', 'lines=*-4')",
        }

    if mode not in {"shift", "replace"}:
        return {"status": False, "message": "mode: Mode must be 'shift' or 'replace'"}

    if len(content) >= 200:
        return {
            "status": False,
            "message": "content: Line length cannot exceed 200 characters",
        }

    return await client.send_query_codebase(
        "write", {"path": path, "lines": lines, "mode": mode, "content": content}
    )
