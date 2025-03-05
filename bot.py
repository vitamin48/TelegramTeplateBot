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
from utils.format_message_info import format_message_info, format_callback_query_info
from services.config import config


async def main():
    # Создаем объекты бота и хранилища состояний
    bot = Bot(token=config.token)
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
    logger.info('Запускаю бот...')
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
