from fastapi import APIRouter, Depends

from src.api.llm_ops.content import router as contentRouter
from src.api.llm_ops.list import router as listRouter
from src.clientmanager import clientManager

router = APIRouter(prefix="/{clientId}")

router.include_router(listRouter)
router.include_router(contentRouter)


@router.get("/")
async def hello(client=Depends(clientManager.get_client)):
    if not client:
        return {"status": False, "message": "Invalid or expired client Id"}

    return {"status": True, "message": f"Client '{client.clientId}' exists"}
