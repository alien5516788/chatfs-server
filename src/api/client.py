from fastapi import APIRouter, WebSocket

from clientmanager.clientmanager import ClientManager

router = APIRouter(prefix="/client")
clientManager = ClientManager()



@router.websocket("/")
async def connect_client(websocket: WebSocket):
    client = await clientManager.add_client(websocket)
    await client.send_acknowledge()

    # Keep socket alive
    try:
        while True:
            message = await websocket.receive_text()
            client.receive_reply(message)

    except Exception:
        print("Log: Client connection unsuccessful")
        pass
