import asyncio

class Client:
    def __init__(self):
        self.commands = CommandHandler()
        
    async def start(self, api):
        self._api = api
        await self._api.start_bot_loop(self.commands)
        
    def run(self, token):
        self._api = APIClient(token)
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.start(self._api))
