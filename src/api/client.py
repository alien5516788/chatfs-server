import asyncio

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from src.socket import client_manager

router = APIRouter(prefix="/client")

_PING_INTERVAL = 20
_TIMEOUT_TOLERANCE = 5


@router.websocket("/")
async def client(socket: WebSocket):
    # Save connection
    client = await client_manager.add_client(socket)

    # Send connect acknowledgement
    await client.send_connect_syn()

    # Client must send replies within given interval (atleast pong)
    # If no reply recieved, timeout happens within next few seconds
    #   and connection get closed and cleaned automatically
    ping_task = asyncio.create_task(client.send_ping(_PING_INTERVAL))

    # Wait for replies
    try:
        while True:
            message = await asyncio.wait_for(
                socket.receive_text(), timeout=_PING_INTERVAL + _TIMEOUT_TOLERANCE
            )

            await client.receive_reply(message)

    except asyncio.TimeoutError:
        print(f"Log: Client timeout ({client.client_id})")

    except WebSocketDisconnect:
        print(f"Log: Client disconnected ({client.client_id})")

    except Exception as e:
        print(f"Unexpected error ({e})")

    finally:
        ping_task.cancel()
        await client_manager.remove_client(client.client_id)
