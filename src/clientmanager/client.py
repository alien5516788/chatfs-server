import asyncio
import json
import os
from copy import deepcopy
from typing import Literal

from fastapi import WebSocket


# New clients should not be created or removed manually
# Instead create or remove them through the client manager
class Client:
    __slots__ = (
        "_sharedContext",
        "_socket",
        "clientId",
    )  # optimizes memory for methods

    _MessageType = Literal["connect_ack", "get_context"]
    _replyType = ["code_context"]

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

    # Messages to client should be sent via handler methods (ex: send_ackknowledge)
    # No message crafting and manual message sending outside should not be done
    # All handler methods should use this private method to insert the basic template and socket communication
    async def _send_message(
        self, status: bool, messageType: _MessageType, message: dict
    ):
        msg = {
            "status": status,
            "message_type": messageType,
        }

        for key, value in message.items():
            msg[key] = value

        await self._socket.send_text(json.dumps(msg))

    # This should only be sent once immediately after the initial connection
    async def send_connect_ack(self):
        await self._send_message(
            True,
            "connect_ack",
            {
                "server_url": f"{os.getenv('SERVER_URL') or 'https://notfound'}/{self.clientId}/",
            },
        )

    # Invoked by LLM endpoints
    # After sending a get context message, the handler should wait until the context is recieved
    # If not recieved within a short time, a timeout happens
    async def _wait_for_context(self):
        while not self._sharedContext:
            await asyncio.sleep(0.01)

    async def send_get_context(
        self, command: str, queries: dict[str, str | bool]
    ) -> dict:
        # Request for context
        await self._send_message(
            True,
            "get_context",
            {"command": command, "queries": queries},
        )

        # Wait for context
        try:
            await asyncio.wait_for(self._wait_for_context(), timeout=2)
        except asyncio.TimeoutError:
            return {
                "status": False,
                "message": "Context wasn't sent by the client or reply timedout",
            }

        # Make a deep copy and revert internal variable to None
        context_copy = deepcopy(self._sharedContext)
        self._sharedContext = None

        return {
            "status": True,
            "context": context_copy,
        }

    # All recived messages should be passed to this method for validation
    # Each message is then passed to individual handler methods for further processing
    # Handler methods are private and should not be used directly
    async def receive_reply(self, reply: str):
        # Pong just resets the timeoutand is only the message that is not json
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
                    "Log: Reply format is not valid (Field 'status' must be a boolean)"
                )
                return

            reply_type = rply.get("reply_type", None)

            if not reply_type:
                print(
                    "Log: Reply format is not valid (required field 'reply_type' not found)"
                )
                return

            if reply_type not in self._replyType:
                print("Log: Reply format is not valid (invalid 'reply_type')")
                return

            # Pass to handlers
            if reply_type == "code_context" and rply.get("context", None):
                self._sharedContext = rply.get("context", None)
                return

        except Exception:
            print("Log: Reply format is not valid")
            return
