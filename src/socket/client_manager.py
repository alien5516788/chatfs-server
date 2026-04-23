import asyncio
from uuid import uuid4

from fastapi import WebSocket

from .client import Client


# Only one client manager instance should exists
# Lifecycle of a client should only be managed by the client manager
class ClientManager:
    def __init__(self):
        self._clients: dict[str, Client] = {}
        self._clients_lock = asyncio.Lock()

    async def add_client(self, socket: WebSocket) -> Client:
        client_id = str(uuid4()).replace("-", "")[
            :15
        ]  # First 15 chars of uuid excluding '-'
        client = await Client.__init_client__(client_id, socket)

        async with self._clients_lock:
            self._clients[client_id] = client

        print(
            f"Log: Client connected (clientId: {client.client_id}, total: {len(self._clients)})"
        )

        return client

    async def get_client(self, client_id: str) -> Client | None:
        async with self._clients_lock:
            return self._clients.get(client_id, None)

    async def remove_client(self, client_id: str):
        async with self._clients_lock:
            self._clients.pop(client_id, None)

        print(
            f"Log: Client removed (clientId: {client_id}), total: {len(self._clients)})"
        )
