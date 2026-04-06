import asyncio
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI

from src.api.client import clientManager
from src.api.client import router as client_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    load_dotenv()

    task = asyncio.create_task(clientManager.clean_clients())
    # TODO: I don't quite understand whats going here, check this later
    try:
        yield

    finally:
        print("Log: Server shutdown")
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass


app = FastAPI(lifespan=lifespan)


app.include_router(client_router)


@app.get("/")
def hello():
    return "Hello from sync server"
