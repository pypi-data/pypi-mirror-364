import asyncio

class Event:
    def __init__(self, bot):
        self.bot = bot
        
    def on_ready(self):
        """Called when the bot is ready to start receiving events"""
        pass
        
    def on_message(self, message):
        """Called when a message is received"""
        pass
        
    def on_command(self, ctx):
        """Called when a command is executed"""
        pass
