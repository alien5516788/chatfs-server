import asyncio
from datetime import datetime, timedelta
from uuid import uuid4

from fastapi import WebSocket

from src.clientmanager.client import Client


# Only one client manager instance should exists
class ClientManager:
    def __init__(self):
        self._connectedClients: dict[str, Client] = {}
        self._clientListLock = asyncio.Lock()

    # Add a new socket connection to the list
    async def add_client(self, socket: WebSocket) -> Client:
        clientId = str(uuid4()).replace("-", "")[:15]
        client = await Client.__init_client__(socket, clientId)

        async with self._clientListLock:
            self._connectedClients[clientId] = client

        print(f"Log: Client connected (clientId: {client.clientId})")

        return client

    # Given the clientId, returns the Client instance from the list
    def get_client(self, clientId: str) -> Client | None:
        client = self._connectedClients.get(clientId)

        return client if client else None

    # Clients should update their hearbeat every 30 seconds, otherwise considered dead
    # This cleanup function checks client heartbeats every 1 minute and removes dead clients
    async def clean_clients(self):
        while True:
            heartRate = datetime.now() - timedelta(seconds=30)
            
            # c
            async with self._clientListLock:
                clientList = list(self._connectedClients.items())

            to_remove = [
                clientId for clientId, client in clientList if client.alive < heartRate
            ]

            # Step 3: remove in batch
            if to_remove:
                async with self._clientListLock:
                    for clientId in to_remove:
                        print(f"Log: Client removed (clientId: {clientId})")
                        self._connectedClients.pop(clientId, None)

            await asyncio.sleep(60)
