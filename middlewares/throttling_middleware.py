from typing import Callable, Dict, Any, Awaitable
from cachetools import TTLCache
from aiogram import BaseMiddleware
from aiogram.types import Message
from services.logger import logger


class ThrottlingMiddleware(BaseMiddleware):
    def __init__(self, slow_mode_delay: float):
        self.cache = TTLCache(maxsize=10_000, ttl=slow_mode_delay)

    async def __call__(self, handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]], event: Message,
                       data: Dict[str, Any]) -> Any:
        if event.chat.id in self.cache:
            logger.info(f"Throttling: User {event.chat.id} request ignored.")
            return
        self.cache[event.chat.id] = True
        return await handler(event, data)
