from typing import Literal

import regex as re
from fastapi import APIRouter, Depends

from src.clientmanager import clientManager
from src.clientmanager.client import Client

createRouter = APIRouter(prefix="/create")
copyRouter = APIRouter(prefix="/copy")
moveRouter = APIRouter(prefix="/move")
deleteRouter = APIRouter(prefix="/delete")
writelineRouter = APIRouter(prefix="/writeline")


@createRouter.get("/")
async def create(
    path: str = "",
    item_type: str = "",
    client: Client = Depends(clientManager.get_client),
):
    if not client:
        return {"status": False, "error": "Invalid or expired client Id"}

    if len(path) <= 0:
        return {
            "status": False,
            "error": "path: Path cannot be empty (e.g. 'path=src/ui', 'path=src/file.txt')",
        }

    if item_type not in {"folder", "file"}:
        return {
            "status": False,
            "error": "item_type: Item type must be 'folder' or 'file'",
        }

    return await client.send_query_codebase(
        "create", {"path": path, "item_type": item_type}
    )


@copyRouter.get("/")
async def copy(
    path: str = "",
    dest_path: str = "",
    client: Client = Depends(clientManager.get_client),
):
    return await _copy_or_move("copy", path, dest_path, client)


@moveRouter.get("/")
async def move(
    path: str = "",
    dest_path: str = "",
    client: Client = Depends(clientManager.get_client),
):
    return await _copy_or_move("move", path, dest_path, client)


async def _copy_or_move(
    cmd: Literal["copy", "move"],
    path: str,
    dest_path: str,
    client: Client,
):
    if not client:
        return {"status": False, "error": "Invalid or expired client Id"}

    if len(path) <= 0:
        return {
            "status": False,
            "error": "path: Path cannot be empty (e.g. 'path=src/ui', 'path=src/file.txt')",
        }

    if len(dest_path) <= 0:
        return {
            "status": False,
            "error": "dest_path: Destination path cannot be empty (e.g. 'path=src/components', 'path=src/test.py')",
        }

    return await client.send_query_codebase(cmd, {"path": path, "dest_path": dest_path})


@deleteRouter.get("/")
async def delete(
    path: str = "",
    client: Client = Depends(clientManager.get_client),
):
    if not client:
        return {"status": False, "error": "Invalid or expired client Id"}

    if len(path) <= 0:
        return {
            "status": False,
            "error": "path: Path cannot be empty (e.g. 'path=src/ui', 'path=src/file.txt')",
        }

    return await client.send_query_codebase("delete", {"path": path})


# Write line command is sent to client as write command
@writelineRouter.get("/")
async def writeline(
    path: str = "",
    line: str = "",
    mode: str = "",
    content: str = "",
    client: Client = Depends(clientManager.get_client),
):
    if not client:
        return {"status": False, "error": "Invalid or expired client Id"}

    if len(path) <= 0:
        return {
            "status": False,
            "error": "path: File name cannot be empty (e.g. 'path=src/file.txt')",
        }

    if not re.match(r"^(\d+|\*)$", line):
        return {
            "status": False,
            "error": "line: Line must be a number or '*' (e.g. 'line=3', 'line=*')",
        }

    if mode not in {"shift", "replace"}:
        return {"status": False, "error": "mode: Mode must be 'shift' or 'replace'"}

    if len(content) >= 200:
        return {
            "status": False,
            "error": "content: Line length cannot exceed 200 characters",
        }

    if "\n" in content:
        return {
            "status": False,
            "error": "content: Content must be a single line (no newline characters are allowed)",
        }

    return await client.send_query_codebase(
        "write",
        {"path": path, "lines": f"{line}-{line}", "mode": mode, "content": content},
    )
