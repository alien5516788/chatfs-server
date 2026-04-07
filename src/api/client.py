import asyncio

from fastapi import APIRouter, WebSocket

from src.clientmanager import clientManager

router = APIRouter(prefix="/client")


@router.websocket("/")
async def connect_client(websocket: WebSocket):
    # Save connection
    client = await clientManager.add_client(websocket)
    await client.send_connect_ack()

    # Client must send heartbeats every 20 seconds
    # If no heartbeat recieved, timeout happens within next 10 seconds
    #   and connection get closed and cleaned automatically
    try:
        while True:
            message = await asyncio.wait_for(websocket.receive_text(), timeout=30)
            await client.receive_reply(message)

    except Exception:
        await clientManager.remove_client(client.clientId)
