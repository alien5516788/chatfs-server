import json
import os
from typing import Literal

from fastapi import WebSocket


# New clients should not be created or removed manually
# Instead create or remove them through the client manager
class Client:
    _MessageType = Literal["connect_ack", "get_context"]
    _replyType = ["code_context"]

    __slots__ = ("_socket", "clientId")  # optimizes memory for methods

    def __init__(self, socket: WebSocket, clientId: str):
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

    # This should only be sent immediately after the initial connection
    async def send_connect_ack(self):
        await self._send_message(
            True,
            "connect_ack",
            {
                "server_url": f"{os.getenv('SERVER_URL') or 'https://notfound'}/{self.clientId}/",
            },
        )

    # Invoked by LLM endpoints
    async def send_get_context(self, command: str, queries: list[str]):
        await self._send_message(
            True,
            "get_context",
            {"command": command, "queries": queries},
        )

    # All recived messages should be passed to this method for validation
    # Each message is then passed to individual handler methods for further processing
    # Handler methods are private and should not be used directly
    def receive_reply(self, reply: str):
        # Pong just resets the timeoutand is only the message that is not json
        # Pong is sent as a response to a socket internel ping
        if reply == "pong":
            return

        # Handle other messages
        try:
            rply = json.loads(reply)

            # Basic format validation
            if "status" not in rply:
                print(
                    "Log: Reply format is not valid (required field 'status' not found)"
                )
                return

            if not isinstance(rply.get("status"), bool):
                print(
                    "Log: Reply format is not valid (Field 'status' must be a boolean)"
                )
                return

            if "reply_type" not in rply:
                print(
                    "Log: Reply format is not valid (required field 'reply_type' not found)"
                )
                return

            if rply.get("reply_type") not in self._replyType:
                print("Log: Reply format is not valid (invalid 'reply_type')")
                return

            # Pass to handlers
            reply_type = rply.get("reply_type")

            if reply_type == "code_context":
                self._recieve_code_context(rply)
                return

        except Exception:
            print("Log: Reply format is not valid")
            return

    # Update shared code context
    def _recieve_code_context(self, reply: dict):
        # TODO: implement this after completing LLM api endpoints
        return
