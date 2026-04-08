import regex as re
from fastapi import APIRouter, Depends

from src.clientmanager import clientManager
from src.clientmanager.client import Client

createRouter = APIRouter(prefix="/create")
copyRouter = APIRouter(prefix="/copy")
moveRouter = APIRouter(prefix="/move")
deleteRouter = APIRouter(prefix="/delete")
insertlineRouter = APIRouter(prefix="/insertline")


@createRouter.get("/")
async def create(
    path: str = "",
    itemtype: str = "",
    client: Client = Depends(clientManager.get_client),
):
    if not client:
        return {"status": False, "message": "Invalid or expired client Id"}

    if len(path) <= 0:
        return {
            "status": False,
            "message": "path: Folder or file name cannot be empty (e.g. 'path=src/ui', 'path=src/file.txt')",
        }

    if itemtype not in {"folder", "file"}:
        return {
            "status": False,
            "message": "itemtype: Item type must be 'folder' or 'file'",
        }

    return await client.send_query_codebase(
        "create", {"path": path, "item_type": itemtype}
    )


@copyRouter.get("/")
async def copy(
    path: str = "",
    destpath: str = "",
    client: Client = Depends(clientManager.get_client),
):
    if not client:
        return {"status": False, "message": "Invalid or expired client Id"}

    if len(path) <= 0:
        return {
            "status": False,
            "message": "path: Path cannot be empty (e.g. 'path=src/ui', 'path=src/file.txt')",
        }

    if len(destpath) <= 0:
        return {
            "status": False,
            "message": "destpath: Destination path cannot be empty (e.g. 'path=src/components', 'path=src/test.py')",
        }

    return await client.send_query_codebase(
        "copy", {"path": path, "dest_path": destpath}
    )


# Exact same structure of copy
@moveRouter.get("/")
async def move(
    path: str = "",
    destpath: str = "",
    client: Client = Depends(clientManager.get_client),
):
    if not client:
        return {"status": False, "message": "Invalid or expired client Id"}

    if len(path) <= 0:
        return {
            "status": False,
            "message": "path: Path cannot be empty (e.g. 'path=src/ui', 'path=src/file.txt')",
        }

    if len(destpath) <= 0:
        return {
            "status": False,
            "message": "destpath: Destination path cannot be empty (e.g. 'path=src/components', 'path=src/test.py')",
        }

    return await client.send_query_codebase(
        "move", {"path": path, "dest_path": destpath}
    )


@deleteRouter.get("/")
async def delete(
    path: str = "",
    client: Client = Depends(clientManager.get_client),
):
    if not client:
        return {"status": False, "message": "Invalid or expired client Id"}

    if len(path) <= 0:
        return {
            "status": False,
            "message": "path: Path cannot be empty (e.g. 'path=src/ui', 'path=src/file.txt')",
        }

    return await client.send_query_codebase("delete", {"path": path})


@insertlineRouter.get("/")
async def insertline(
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
        "insertline", {"path": path, "lines": lines, "mode": mode, "content": content}
    )
