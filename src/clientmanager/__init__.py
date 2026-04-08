from .clientmanager import ClientManager

# Shared client manager instance
# Make sure only 1 worker process runs, otherwise same instance won't be available to all endpoints
clientManager = ClientManager()
