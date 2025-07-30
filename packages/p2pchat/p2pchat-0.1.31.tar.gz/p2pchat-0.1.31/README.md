# P2PChat

A Python library for creating P2P chat bots with async support.

## Installation

```bash
pip install p2pchat
```

## Quick Start

```python
from p2pchat import Bot

# Create a bot instance
bot = Bot(prefix='$')

@bot.command()
async def hello(ctx):
    message = ctx.get('message')
    username = message.get('username', 'Unknown User')
    await ctx.get('api').send_message(f"Hello {username}!", ctx.get('chat_id'))

@bot.command()
async def checkstaff(ctx):
    args = ctx.get('args')
    if args:
        username = args[0]
        user_data = await ctx.get('api').get_user_data(username)
        if user_data:
            is_staff = user_data.get('is_staff', False)
            message = f"{username} is a staff member!" if is_staff else f"{username} is not a staff member."
        else:
            message = f"User {username} not found."
    else:
        message = "Usage: $checkstaff <username>"
    
    await ctx.get('api').send_message(message, ctx.get('chat_id'))

# Run the bot
if __name__ == "__main__":
    bot.run("your_bot_token_here")
```

## Features

- **Async Support**: Built with asyncio for high performance
- **Command System**: Easy-to-use command decorators
- **User Management**: Check user permissions and data
- **Message Handling**: Send and receive messages
- **Staff Commands**: Built-in support for staff-only commands

## Commands

### Built-in Commands

- `$hello` - Greet users
- `$checkstaff <username>` - Check if a user is staff
- `$clear <target>` - Clear chat messages (staff only)
- `$announce <target> <message>` - Send announcements (staff only)

## API Reference

### Bot Class

```python
Bot(prefix='$')
```

Create a new bot instance.

**Parameters:**
- `prefix` (str): Command prefix (default: '$')

### Command Decorator

```python
@bot.command()
async def command_name(ctx):
    # Command logic here
    pass
```

Register a new command.

**Context (ctx) contains:**
- `message`: The message object
- `chat_id`: ID of the chat
- `args`: Command arguments as a list
- `api`: API client for making requests

### API Methods

```python
# Send a message
await ctx.get('api').send_message(content, chat_id)

# Get user data
user_data = await ctx.get('api').get_user_data(username)

# Get bot info
bot_info = await ctx.get('api').get_bot_info()
```

## Requirements

- Python 3.7+
- aiohttp

## License

MIT License

## Support

- Website: [p2pchat.info](https://p2pchat.info)
- Documentation: [p2pchat.info](https://p2pchat.info)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
