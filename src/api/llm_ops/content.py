import regex as re
from fastapi import APIRouter, Depends, HTTPException, Query

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
        return {"status": False, "message": "Invalid or expired client Id"}

    if len(path) <= 0:
        return {
            "status": False,
            "message": "path: File name cannot be empty (e.g. 'path=file.config.json', 'path=src/file.txt')",
        }

    if not re.match(r"^(\d+|\*)-(\d+|\*)$", lines):
        return {
            "status": False,
            "message": "lines: Lines must follow the pattern '^(\\d+|\\*)-(\\d+|\\*)$' (e.g. 'lines=1-*', 'lines=3-6', 'lines=*-4')",
        }

    return await client.send_get_context("content", {"path": path, "lines": lines})
