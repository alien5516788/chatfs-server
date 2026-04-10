import regex as re
from fastapi import APIRouter, Depends

from src.clientmanager import clientManager
from src.clientmanager.client import Client

router = APIRouter(prefix="/content")


@router.get("/")
async def content(
    path: str = "",
    lines: str = "1-*",
    client: Client = Depends(clientManager.get_client),
):
    if not client:
        return {"status": False, "error": "Invalid or expired client Id"}

    if len(path) <= 0:
        return {
            "status": False,
            "error": "path: Path must be a file and cannot be empty (e.g. 'path=file.config.json', 'path=src/file.txt')",
        }

    if not re.match(r"^(\d+|\*)-(\d+|\*)$", lines):
        return {
            "status": False,
            "error": "lines: Lines must follow the pattern 'start-end' (e.g. lines=2-2, 'lines=1-*', 'lines=3-6', 'lines=*-4', lines=*-*)",
        }

    return await client.send_query_codebase(
        "content", {"path": path, "lines": "1-*" if lines == "*-*" else lines}
    )
