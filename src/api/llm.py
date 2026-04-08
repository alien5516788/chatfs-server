from fastapi import APIRouter, Depends

from src.api.llm_ops.content import router as contentRouter
from src.api.llm_ops.list import router as listRouter
from src.api.llm_ops.manipulations import (
    copyRouter,
    createRouter,
    deleteRouter,
    moveRouter,
    writelineRouter,
)
from src.api.llm_ops.write import router as writeRouter
from src.clientmanager import clientManager

router = APIRouter(prefix="/{clientId}")

router.include_router(listRouter)
router.include_router(contentRouter)
router.include_router(createRouter)
router.include_router(copyRouter)
router.include_router(moveRouter)
router.include_router(deleteRouter)
router.include_router(writelineRouter)
router.include_router(writeRouter)


@router.get("/")
async def hello(client=Depends(clientManager.get_client)):
    if not client:
        return {"status": False, "message": "Invalid or expired client Id"}

    return {"status": True, "message": f"Client '{client.clientId}' exists"}
