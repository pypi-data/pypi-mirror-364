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
        async with session.get(self.base_url, params=params) as response:
            data = await response.json()
            logger.debug(f"API Response: {data}")
            # Update last_check if we have messages
            messages = data.get('messages', [])
            if messages:
                for message in messages:
                    if 'timestamp' in message:
                        self.last_check = max(self.last_check, message['timestamp'])
            return data

    async def send_message(self, content, chat_id=None):
        logger.debug(f"Sending message to chat {chat_id}: {content}")
        session = await self._ensure_session()
        data = {'content': content}
        if chat_id:
            data['chat_id'] = chat_id
        async with session.post(self.base_url, json=data) as response:
            return await response.json()

    def __init__(self, token):
        self.token = token
        self.base_url = 'http://p2pchat.info/login/Bots/api/bot_endpoint.php'
        self.headers = {'Authorization': f'Bot {token}'}
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
        async with session.get(self.base_url, params=params) as response:
            data = await response.json()
            return data



    async def get_user_data(self, username):
        session = await self._ensure_session()
        params = {'username': username}
        async with session.get(self.base_url, params=params) as response:
            data = await response.json()
            return data.get('user')




