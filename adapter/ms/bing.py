import os
from typing import Generator

from adapter.botservice import BotAdapter
from EdgeGPT import Chatbot as EdgeChatbot

from constants import botManager
from exceptions import BotOperationNotSupportedException
import tempfile
import json
from loguru import logger
class BingAdapter(BotAdapter):
    cookieData = None
    cookieFile = None

    bot: EdgeChatbot
    """实例"""

    def __init__(self):
        account = botManager.pick('bing-cookie')
        self.cookieData = []
        for line in account.cookie_content.split("; "):
            key, value = line.split("=", 1)
            self.cookieData.append({"name": key, "value": value})

        self.cookieFile = tempfile.NamedTemporaryFile(mode='w', suffix=".json", encoding='utf8', delete=False)
        self.cookieFile.write(json.dumps(self.cookieData))
        self.cookieFile.close()
        self.bot = EdgeChatbot(self.cookieFile.name)
    def __del__(self):
        logger.debug("[Bing] 释放 Cookie 文件……")
        os.remove(self.cookieFile.name)
    async def rollback(self):
        raise BotOperationNotSupportedException()

    async def on_reset(self):
        await self.bot.reset()
        self.cookieData.delete()

    async def ask(self, prompt: str) -> Generator[str, None, None]:
        async for response in self.bot.ask_stream(prompt):
            yield response