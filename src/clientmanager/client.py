import json
import os
from datetime import datetime
from typing import Literal

from fastapi import WebSocket


# New clients should not be created manually
# Instead create them through the client manager
class Client:
    _MessageType = Literal["connect_ack", "get_context", "general"]
    _replyType = ["heart_beat", "code_context"]

    __slots__ = ("_socket", "clientId", "alive")  # optimizes memory for methods

    def __init__(self, socket: WebSocket, clientId: str):
        self._socket: WebSocket = socket
        self.clientId: str = clientId
        self.alive: datetime = datetime.now()

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
    async def send_acknowledge(self):
        await self._send_message(
            True,
            "connect_ack",
            {
                "client_id": self.clientId,
                "server_url": os.getenv("SERVER_URL"),
            },
        )

    # All recived messages should be passed to this method for validation
    # Each message is then passed to individual handler methods for further processing
    # Handler methods are private and should not be used directly
    def receive_reply(self, reply: str):
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

            if reply_type == "heart_beat":
                self._recieve_heart_beat()

            if reply_type == "code_context":
                self._recieve_code_context(rply)

        except Exception:
            print("Log: Reply format is not valid")
            return

    # Update socket alive
    def _recieve_heart_beat(self):
        self.alive = datetime.now()

    # Update shared code context
    def _recieve_code_context(self, reply: dict):
        # TODO: implement this after completing LLM api endpoints
        pass
