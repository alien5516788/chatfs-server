import asyncio
import json
import os
from typing import Literal

from fastapi import WebSocket

MessageType = Literal["connect_ack", "get_context"]
replyTypes = {"code_context"}


# New clients should not be created or removed manually
# Instead create or remove them through the client manager
class Client:
    __slots__ = (
        "_sharedContext",
        "_socket",
        "clientId",
    )  # optimizes memory for methods

    def __init__(self, socket: WebSocket, clientId: str):
        self._sharedContext: dict | None = None
        self._socket: WebSocket = socket
        self.clientId: str = clientId

    # Client is initialized through a class method
    # Becuase the initializing process is async
    @classmethod
    async def __init_client__(cls, socket: WebSocket, clientId: str):
        await socket.accept()
        return cls(socket, clientId)

    # Messages to socket should be sent via handler methods (ex: send_ackknowledge)
    # No message crafting and manual message sending outside the client object should not be done

    # This should only be sent once immediately after the initial connection
    async def send_connect_ack(self):
        message_type: MessageType = "connect_ack"
        message = {
            "status": True,
            "message_type": message_type,
            "server_url": f"{os.getenv('SERVER_URL') or 'https://notfound'}/{self.clientId}/",
        }

        await self._socket.send_text(json.dumps(message))

    # Invoked by LLM endpoints
    # After sending a get context message, the handler should wait until the context is recieved
    # Message get timedout if not recieved withing 2 seconds
    async def __wait_for_context(self):
        while not self._sharedContext:
            await asyncio.sleep(0.01)

    async def send_get_context(
        self, command: str, queries: dict[str, int | float | str | bool]
    ) -> dict:
        # Clean old shared contexts
        self._sharedContext = None

        # Request for context
        message_type: MessageType = "get_context"
        message = {
            "status": True,
            "message_type": message_type,
            "command": command,
            "queries": queries,
        }

        await self._socket.send_text(json.dumps(message))

        # Wait for context
        try:
            await asyncio.wait_for(self.__wait_for_context(), timeout=2)
        except asyncio.TimeoutError:
            return {
                "status": False,
                "message": "Context wasn't sent by the client or timeout occured",
            }

        return {
            "status": True,
            "context": self._sharedContext,
        }

    # All recived messages should be passed to this method for validation
    # Each message is then passed to individual handler methods for further processing
    # Handler methods are private and should not be used directly
    async def receive_reply(self, reply: str):
        # Pong just resets the timeout and is only the message that is not JSON
        # Pong is sent as a response to a socket internel ping
        if reply == "pong":
            return

        # Handle other messages
        try:
            rply = json.loads(reply)

            # Basic format validation
            status = rply.get("status", None)

            if not status:
                print(
                    "Log: Reply format is not valid (required field 'status' not found)"
                )
                return

            if not isinstance(status, bool):
                print(
                    "Log: Reply format is not valid (field 'status' must be a boolean)"
                )
                return

            reply_type = rply.get("reply_type", None)

            if not reply_type:
                print(
                    "Log: Reply format is not valid (required field 'reply_type' not found)"
                )
                return

            if reply_type not in replyTypes:
                print("Log: Reply format is not valid (invalid 'reply_type')")
                return

            # Pass to handlers
            if reply_type == "code_context" and rply.get("context", None):
                self._sharedContext = rply.get("context", None)
                return

        except Exception:
            print("Log: Reply format is not valid")
            return
