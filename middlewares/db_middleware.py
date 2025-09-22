import aiosqlite
from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject


class DbSessionMiddleware(BaseMiddleware):
    def __init__(self, db_path: str):
        super().__init__()
        self.db_path = db_path

    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any]
    ) -> Any:
        # Открываем асинхронное соединение с базой данных
        async with aiosqlite.connect(self.db_path) as db:
            # Передаем объект соединения 'db' в хэндлеры через словарь 'data'
            data['db'] = db
            # Вызываем следующий обработчик в цепочке и ждем результата
            return await handler(event, data)
