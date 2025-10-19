import os
import asyncio
import traceback
from io import BytesIO
from dotenv import load_dotenv
from aiogram import Bot
from aiogram.types import BufferedInputFile
from aiogram.exceptions import TelegramBadRequest

from services.config import load_config
from services.logger import logger

load_dotenv()


async def generate_demo_task(ctx, task_data: dict):
    """
    Асинхронная задача для генерации отчета.
    Выполняется в воркере arq, чтобы не блокировать бота.
    """
    chat_id = task_data.get("chat_id")
    status_msg_id = task_data.get("status_msg_id")

    config = load_config()
    bot = Bot(token=config.token, parse_mode='HTML')

    try:
        # 1. Симуляция работы тяжелой задачи
        await asyncio.sleep(5)

        # 2. Отправка результата
        logger.info(f"Успешно.")

    except Exception as e:
        error_text = f"Ошибка в воркере для чата {chat_id}: {e}"
        logger.error(error_text, exc_info=True)
        user_error_message = "❌ Произошла ошибка. Попробуйте позже."
        try:
            await bot.edit_message_text(user_error_message, chat_id=chat_id, message_id=status_msg_id)
        except TelegramBadRequest:
            await bot.send_message(chat_id, user_error_message)

        # Отправка подробного отчета об ошибке в лог-чат
        if config.logs_chat:
            try:
                error_details_for_log = (
                    f"‼️ Ошибка в воркере arq!\n\n"
                    f"👤 Чат: {chat_id}\n"
                    f"Класс ошибки: {type(e).__name__}\n"
                    f"Сообщение: {e}\n\n"
                    f"--- Трейсбек ---\n"
                    f"{traceback.format_exc()}"
                )
                error_file = BufferedInputFile(error_details_for_log.encode('utf-8'), filename="worker_error.txt")
                await bot.send_document(config.logs_chat, error_file, caption="‼️ Ошибка в воркере")
            except Exception as log_e:
                logger.critical(f"КРИТИЧЕСКАЯ ОШИБКА: Не удалось отправить лог ошибки в чат! Ошибка: {log_e}")

    finally:
        await bot.session.close()


# --- Настройки для ARQ Worker ---
class WorkerSettings:
    """
    Конфигурация для запуска воркера Arq.
    Для запуска используйте команду в терминале: arq worker.WorkerSettings
    """
    redis_host = os.getenv("REDIS_HOST", "localhost")
    redis_port = int(os.getenv("REDIS_PORT", 6379))
    functions = [generate_demo_task]  # Список задач, которые может выполнять воркер
    max_jobs = 2  # Количество задач, выполняемых одновременно
    queue_name = 'default'  # Название очереди
