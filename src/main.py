from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI

from src.api.client import router as clientRouter
from src.api.llm import router as llmRouter


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup tasks
    load_dotenv()

    print("Log: Server started")

    yield

    # Shutdown tasks
    print("Log: Server shutdown")


app = FastAPI(lifespan=lifespan)

# Assign routing groups
app.include_router(clientRouter)
app.include_router(llmRouter)
