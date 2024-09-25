import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.types import Message, BotCommand
from aiogram.filters import CommandStart
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import CallbackQuery
from aiogram import F

from handlers import commands, universal_handler
from services.logger import logger

from services.queries import add_user, get_lexicon
from services.utils import format_message_info, format_callback_query_info
from services.config import TOKEN, ADMINS_ID, LOGS_CHATS_ID


async def main():
    # Создаем объекты бота и хранилища состояний
    bot = Bot(token=TOKEN)
    storage = MemoryStorage()

    # Создаем диспетчер
    dp = Dispatcher(storage=storage)
    # Устанавливаем команды для бота
    await bot.set_my_commands([
        BotCommand(command="/start", description="Start BOT"),
    ])

    dp.include_router(commands.send_command)
    dp.include_router(universal_handler.unihandler)

    # Запускаем polling
    await dp.start_polling(bot)
    logger.info('Бот запущен')


if __name__ == "__main__":
    asyncio.run(main())
