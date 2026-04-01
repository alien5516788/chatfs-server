from time import sleep

from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def root():
    return {"message": "Hello from sync server"}


@app.get("/command/{name}")
def get_command(name: str):
    sleep(6)
    return {"command": f"You waited for '{name}'"}
