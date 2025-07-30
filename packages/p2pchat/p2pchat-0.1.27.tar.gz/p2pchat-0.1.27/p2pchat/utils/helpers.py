import asyncio

async def execute_command(func, ctx):
    """Execute command functions asynchronously"""
    if asyncio.iscoroutinefunction(func):
        return await func(ctx)
    return func(ctx)

def parse_command(message, prefix='!'):
    """Parse message content into command and arguments"""
    content = message.get('message', '').strip()
    if not content.startswith(prefix):
        return None, []
        
    parts = content[len(prefix):].split()
    command = parts[0].lower()
    args = parts[1:]
    
    return command, args
