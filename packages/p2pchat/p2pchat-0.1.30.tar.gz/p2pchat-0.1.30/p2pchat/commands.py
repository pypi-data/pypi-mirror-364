class Context:
    def __init__(self, bot, message):
        self.bot = bot
        self.message = message
        
    async def send(self, content):
        await self.bot._api.send_message(self.message.chat_id, content)

class Command:
    def __init__(self, func, name):
        self.callback = func
        self.name = name

class CommandHandler:
    def __init__(self):
        self.commands = {}
        
    def add_command(self, name, func):
        self.commands[name] = Command(func, name)