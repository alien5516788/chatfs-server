from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def root():
    return {"message": "Hello from sync server"}


@app.get("/command/{name}")
def get_command(name: str):
    return {"command": f"You searched for '{name}'"}
