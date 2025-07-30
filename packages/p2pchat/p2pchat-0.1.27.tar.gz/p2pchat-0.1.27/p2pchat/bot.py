import asyncio
from .api.endpoints import APIClient
from .commands import CommandHandler
from .utils.helpers import parse_command, execute_command

class Bot:
    def __init__(self, prefix=None):
        self.command_handler = CommandHandler()
        self.prefix = prefix if prefix is not None else '!'
        
    async def get_username(self):
        messages = await self.api_client.get_messages()
        if messages and 'bot_info' in messages:
            return messages['bot_info']['username']
        return 'Unknown'

    async def get_bot_info(self):
        response = await self.api_client.get_bot_info()
        if response and 'bot_info' in response:
            return response['bot_info']['username']
        return 'Unknown'

    def command(self):
        def decorator(func):
            name = func.__name__
            self.command_handler.add_command(name, func)
            return func
        return decorator

    async def process_messages(self):
        processed_messages = set()
        
        while True:
            messages = await self.api_client.get_messages()
            for message in messages.get('messages', []):
                message_id = message.get('id')
                if message_id not in processed_messages:
                    command, args = parse_command(message, prefix=self.prefix)
                    if command and command in self.command_handler.commands:
                        ctx = {
                            'message': message,
                            'chat_id': message.get('chat_id'),
                            'args': args,
                            'api': self.api_client
                        }
                        await execute_command(self.command_handler.commands[command].callback, ctx)
                        processed_messages.add(message_id)
            await asyncio.sleep(0.1)

    def run(self, token):
        self.api_client = APIClient(token)
        loop = asyncio.get_event_loop()
        try:
            username = loop.run_until_complete(self.get_bot_info())
            banner = """
        ===============================
        |       P2P CHAT BOT        |
        ===============================
            """
            print(banner)
            print("Bot is now online!")
            print(f"Username: {username}")
            print("===============================")
            loop.run_until_complete(self.process_messages())
        except KeyboardInterrupt:
            loop.close()