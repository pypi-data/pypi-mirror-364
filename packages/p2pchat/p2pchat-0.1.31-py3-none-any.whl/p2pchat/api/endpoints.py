import aiohttp
from datetime import datetime
import asyncio
import logging

logger = logging.getLogger(__name__)

class APIClient:
    async def get_messages(self):
        logger.debug("Fetching messages from API")
        session = await self._ensure_session()
        params = {'last_check': self.last_check}
        print(f"[DEBUG] Requesting messages with last_check: {self.last_check}")
        async with session.get(self.base_url, params=params, headers=self.headers) as response:
            data = await response.json()
            logger.debug(f"API Response: {data}")
            print(f"[DEBUG] Got {len(data.get('messages', []))} messages")
            # Update last_check if we have messages
            messages = data.get('messages', [])
            if messages:
                print(f"[DEBUG] Processing {len(messages)} messages")
                for message in messages:
                    print(f"[DEBUG] Message: {message}")
                    if 'timestamp' in message:
                        # Convert timestamp string to unix timestamp
                        timestamp = message['timestamp']
                        if isinstance(timestamp, str):
                            try:
                                # Convert datetime string to unix timestamp
                                from datetime import datetime
                                dt = datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S')
                                timestamp = int(dt.timestamp())
                            except (ValueError, TypeError):
                                timestamp = 0
                        elif isinstance(timestamp, int):
                            # Already an integer timestamp
                            pass
                        else:
                            timestamp = 0
                        self.last_check = max(self.last_check, timestamp)
            return data

    async def send_message(self, content, chat_id=None):
        logger.debug(f"Sending message to chat {chat_id}: {content}")
        session = await self._ensure_session()
        data = {'content': content}
        if chat_id:
            data['chat_id'] = chat_id
        async with session.post(self.base_url, json=data, headers=self.headers) as response:
            return await response.json()

    def __init__(self, token):
        self.token = token
        self.base_url = 'http://p2pchat.info/login/Bots/api/bot_endpoint.php'
        self.headers = {'X-Bot-Token': token}
        self.session = None
        self.last_check = 0
        
    async def _get_session(self):
        if not hasattr(self, 'session'):
            self.session = aiohttp.ClientSession(headers=self.headers)
        return self.session

    async def _create_session(self):
        return aiohttp.ClientSession(headers=self.headers)


    async def _ensure_session(self):
        if self.session is None:
            self.session = aiohttp.ClientSession(headers=self.headers)
        return self.session

    async def get_bot_info(self):
        session = await self._ensure_session()
        params = {'bot_info': '1'}
        async with session.get(self.base_url, params=params, headers=self.headers) as response:
            data = await response.json()
            return data



    async def get_user_data(self, username):
        session = await self._ensure_session()
        params = {'username': username}
        async with session.get(self.base_url, params=params, headers=self.headers) as response:
            data = await response.json()
            return data.get('user')

    async def close(self):
        """Close the aiohttp session to prevent unclosed client warnings"""
        if self.session:
            await self.session.close()
            self.session = None

