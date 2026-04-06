import asyncio
from uuid import uuid4

from fastapi import WebSocket

from .client import Client


# Only one client manager instance should exists
class Manager:
    def __init__(self):
        self._connectedClients: dict[str, Client] = {}
        self._clientListLock = asyncio.Lock()

    # Add a new socket connection to the list
    async def add_client(self, socket: WebSocket) -> Client:
        clientId = str(uuid4()).replace("-", "")[:15]
        client = await Client.__init_client__(socket, clientId)

        async with self._clientListLock:
            self._connectedClients[clientId] = client
        print(
            f"Log: Client connected (clientId: {client.clientId}, total: {len(self._connectedClients)})"
        )

        return client

    # Given the clientId, returns the Client instance from the list
    async def get_client(self, clientId: str) -> Client | None:
        async with self._clientListLock:
            return self._connectedClients.get(clientId, None)

    # Remove a socket connection from the list
    async def remove_client(self, clientId: str):
        async with self._clientListLock:
            self._connectedClients.pop(clientId, None)
        print(
            f"Log: Client removed (clientId: {clientId}), total: {len(self._connectedClients)}"
        )
