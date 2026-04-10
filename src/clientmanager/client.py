import asyncio
import json
import os
from typing import Literal
from uuid import uuid4

from fastapi import WebSocket

# TODO: Rename query_code base to query_workspace
MessageType = Literal["connect_ack", "query_codebase"]
replyTypes = {"code_context"}


# New clients should not be created or removed manually
# Instead create or remove them through the client manager
class Client:
    __slots__ = (
        "clientId",
        "_socket",
        "_shared_context",
        "_shared_context_lock",
    )  # optimizes memory for methods

    def __init__(self, clientId: str, socket: WebSocket):
        self.clientId: str = clientId
        self._socket: WebSocket = socket
        self._shared_context: dict[str, asyncio.Future] = {}
        self._shared_context_lock = asyncio.Lock()

    # Client is initialized through a class method
    # Becuase the initializing process is async
    @classmethod
    async def __init_client__(cls, clientId: str, socket: WebSocket):
        await socket.accept()
        return cls(clientId, socket)

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
    # After sending a get codebase message, the handler should wait until the code context is recieved
    # Message get timedout if not recieved withing 2 seconds
    async def send_query_codebase(
        self, command: str, queries: dict[str, int | float | str | bool]
    ) -> dict:
        # Message id
        message_id = str(uuid4())

        # Create a future varible to store shared context
        loop = asyncio.get_running_loop()
        future = loop.create_future()

        # Add future entry to shared contexts
        async with self._shared_context_lock:
            self._shared_context[message_id] = future

        # Query codebase
        message_type: MessageType = "query_codebase"
        message = {
            "id": message_id,
            "status": True,
            "message_type": message_type,
            "command": command,
            "queries": queries,
        }

        await self._socket.send_text(json.dumps(message))

        # Wait for context
        try:
            context = await asyncio.wait_for(future, timeout=4)

        except asyncio.TimeoutError:
            async with self._shared_context_lock:
                self._shared_context.pop(message_id, None)

            return {"status": False, "error": "Context wasn't sent or timeout occured"}

        async with self._shared_context_lock:
            self._shared_context.pop(message_id, None)

        return context

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
            rply: dict = json.loads(reply)

            # Basic format validation
            message_id = rply.get("id", None)

            if not message_id:
                print("Log: Reply format is not valid (required field 'id' not found)")
                return

            if not isinstance(message_id, str):
                print("Log: Reply format is not valid (field 'id' is not a string)")
                return

            status = rply.get("status", None)

            if status is None:
                print(
                    "Log: Reply format is not valid (required field 'status' not found)"
                )
                return

            if not isinstance(status, bool):
                print(
                    "Log: Reply format is not valid (field 'status' is not a boolean)"
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
            if reply_type == "code_context":
                async with self._shared_context_lock:
                    future = self._shared_context.pop(message_id, None)

                if future is None:
                    print(f"Log: Late response ignored ({message_id})")
                    return

                if not future.done():
                    future.set_result(rply.get("context", None))

                return

        except Exception:
            print("Log: Reply format is not valid")
            return
