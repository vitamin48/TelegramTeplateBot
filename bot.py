import asyncio
import asyncpg
import os
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand
from aiogram.fsm.storage.redis import RedisStorage
import redis.asyncio as redis
from arq import create_pool as create_arq_pool
from arq.connections import RedisSettings

from handlers import (
    commands,
    universal_handler,
    broadcast,
    report_handler,
    errors
)
from services.logger import logger
from services.config import load_config, DATABASE_URL
from middlewares.db_middleware import DbSessionMiddleware
from middlewares.throttling_middleware import ThrottlingMiddleware

load_dotenv()


async def main():
    config = load_config()

    # Инициализация Redis для FSM и Arq
    redis_pool = redis.from_url(f"redis://{config.redis_host}:{config.redis_port}/0")
    storage = RedisStorage(redis=redis_pool)
    arq_redis_settings = RedisSettings(host=config.redis_host, port=config.redis_port)
    arq_pool = await create_arq_pool(arq_redis_settings)

    # Инициализация пула соединений с PostgreSQL
    pool = await asyncpg.create_pool(dsn=DATABASE_URL)

    # Инициализация бота и диспетчера
    bot = Bot(token=config.token, parse_mode='HTML')
    dp = Dispatcher(
        storage=storage,
        config=config,
        pool=pool,
        arq_pool=arq_pool
    )

    # Регистрация middlewares
    dp.update.middleware(DbSessionMiddleware(pool=pool))
    throttling_middleware = ThrottlingMiddleware(slow_mode_delay=1.0)
    dp.message.middleware(throttling_middleware)
    dp.callback_query.middleware(throttling_middleware)

    # Установка команд бота
    await bot.set_my_commands([
        BotCommand(command="/start", description="Начать работу"),
        BotCommand(command="/help", description="❓ Помощь"),
        BotCommand(command="/report", description="Сгенерировать отчет (пример фоновой задачи)"),
    ])

    # Подключение роутеров
    dp.include_router(errors.errors_router)
    dp.include_router(commands.router)
    dp.include_router(broadcast.router)
    dp.include_router(report_handler.router)
    dp.include_router(universal_handler.unihandler)

    try:
        logger.info('Запускаю бот...')
        await dp.start_polling(bot)
    finally:
        logger.info('Бот остановлен.')
        await dp.storage.close()
        await pool.close()
        if arq_pool:
            await arq_pool.close()


if __name__ == "__main__":
    asyncio.run(main())
