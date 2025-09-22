import asyncio
from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand
from aiogram.fsm.storage.memory import MemoryStorage

from handlers import commands, universal_handler, broadcast
from services.logger import logger
from services.config import load_config  # Импортируем асинхронный загрузчик
from middlewares.db_middleware import DbSessionMiddleware  # Импортируем middleware
from handlers.errors import errors_router


async def main():
    # Асинхронно загружаем конфигурацию из БД
    config = await load_config("db_bot.db")

    # Создаем объекты бота и хранилища состояний
    bot = Bot(token=config.token)
    storage = MemoryStorage()

    # Создаем диспетчер
    dp = Dispatcher(storage=storage, config=config)
    dp.update.middleware(DbSessionMiddleware(db_path="db_bot.db"))

    # Устанавливаем команды для бота
    await bot.set_my_commands([
        BotCommand(command="/start", description="Start BOT"),
    ])

    # Подключаем роутеры
    dp.include_router(errors_router)
    dp.include_router(commands.send_command)
    dp.include_router(broadcast.router)
    dp.include_router(universal_handler.unihandler)

    # Запускаем polling
    logger.info('Запускаю бот...')
    # Удаляем старые вебхуки и запускаем бота
    # await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
