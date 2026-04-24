import asyncio
import json
import os
from uuid import uuid4

from fastapi import WebSocket
from pydantic import ValidationError

from src.types import (
    ConnectAck,
    ConnectSyn,
    LlmCommand,
    LlmResponse,
    LlmResult,
    Ping,
    Pong,
)


class Client:
    __slots__ = (
        "client_id",
        "_socket",
        "_llm_results",
        "_llm_results_lock",
    )

    _REPLY_TIMEOUT = 5

    def __init__(self, client_id: str, socket: WebSocket):
        self.client_id: str = client_id
        self._socket: WebSocket = socket

        # LLM command results
        self._llm_results: dict[str, asyncio.Future] = {}
        self._llm_results_lock = asyncio.Lock()

    # Client is initialized through a class method
    # Becuase the initializing process is async
    @classmethod
    async def __init_client__(cls, clientId: str, socket: WebSocket):
        await socket.accept()
        return cls(clientId, socket)

    # This should only be sent once immediately after the initial connection
    async def send_connect_syn(self):
        message = ConnectSyn(
            status=True,
            message_type="connect_syn",
            gateway_url=f"{os.getenv('SERVER_URL') or 'https://notfound'}/{self.client_id}/",
        )

        try:
            await self._socket.send_text(json.dumps(message.model_dump()))
        except Exception:
            pass

    # This must be send repeatedly with an interval to keep connection alive
    async def send_ping(self, interval: int):
        try:
            message = Ping(status=True, message_type="ping")
            while True:
                # Adjust ping interval to account for latency
                s = asyncio.get_running_loop().time()

                try:
                    await self._socket.send_text(json.dumps(message.model_dump()))
                except Exception:
                    break

                e = asyncio.get_event_loop().time() - s
                await asyncio.sleep(max(0, interval - e))

        except asyncio.CancelledError:
            pass

    # This is called by the LLM
    # Reply is expected and returned
    async def send_llm_command(
        self, command: str, params: dict[str, str]
    ) -> LlmResponse:
        # Message id
        message_id = str(uuid4())

        # Create a future variable to store reply
        loop = asyncio.get_running_loop()
        future = loop.create_future()

        # Add future entry for reply
        async with self._llm_results_lock:
            self._llm_results[message_id] = future

        # Send message
        message = LlmCommand(
            status=True,
            message_type="llm_command",
            id=message_id,
            command=command,
            params=params,
        )

        try:
            await self._socket.send_text(json.dumps(message.model_dump()))
        except Exception:
            async with self._llm_results_lock:
                self._llm_results.pop(message_id, None)

            return LlmResponse(status=False, result="Failed to send command to client")

        # Wait for reply
        try:
            return await asyncio.wait_for(future, timeout=self._REPLY_TIMEOUT)

        except asyncio.TimeoutError:
            async with self._llm_results_lock:
                self._llm_results.pop(message_id, None)

            future.cancel()

            return LlmResponse(
                status=False, result="Reply wasn't recieved or timeout occured"
            )

    # Recieved replies are handled here
    async def receive_reply(self, reply: str):
        # Connect acknowledgement
        try:
            _ = ConnectAck.model_validate_json(reply)
            print(f"Log: ConnectAck received ({self.client_id})")
            return

        except ValidationError:
            pass

        # Pong
        try:
            _ = Pong.model_validate_json(reply)
            print(f"Log: Pong received ({self.client_id})")
            return

        except ValidationError:
            pass

        # LLMResult
        try:
            rply = LlmResult.model_validate_json(reply)

            async with self._llm_results_lock:
                future = self._llm_results.pop(rply.id, None)

            if future is None:
                print(f"Log: Late response ignored ({rply.id})")
                return

            if not future.done():
                reply_unwrapped = LlmResponse(status=rply.status, result=rply.result)
                future.set_result(reply_unwrapped)

        except ValidationError:
            print("Log: Invalid response format")
