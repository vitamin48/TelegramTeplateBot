import logging
import traceback
import html
from io import BytesIO

from aiogram import Router, F, Bot
from aiogram.types import ErrorEvent, BufferedInputFile
from aiogram.exceptions import TelegramBadRequest

from services.config import Config


errors_router = Router()


@errors_router.error(F.exception)
async def handle_all_errors(event: ErrorEvent, bot: Bot, config: Config):
    """
    Глобальный обработчик ошибок.
    Ловит все ошибки и отправляет подробное сообщение в чат логов.
    """
    if not config.logs_chat:
        logging.error(f"Error chat not specified. Update: {event.update.model_dump_json(indent=2, exclude_none=True)}")
        logging.exception(event.exception)
        return

    # Экранируем данные
    error_text = html.escape(str(event.exception))
    traceback_text = html.escape(traceback.format_exc())
    update_json_text = html.escape(event.update.model_dump_json(indent=2, exclude_none=True))

    error_message = (
        f"‼️ <b>Произошла ошибка!</b>\n\n"
        f"<b>Тип:</b> {type(event.exception).__name__}\n"
        f"<b>Ошибка:</b>\n<pre>{error_text}</pre>\n\n"
        f"<b>Traceback:</b>\n<pre>{traceback_text}</pre>\n\n"
        f"<b>Update:</b>\n<pre>{update_json_text}</pre>"
    )

    try:
        if len(error_message) > 4096:
            # Формируем контент для файла (уже без HTML-тегов)
            error_doc_content = (
                f"Тип: {type(event.exception).__name__}\n"
                f"Ошибка: {str(event.exception)}\n\n"
                f"Traceback:\n{traceback.format_exc()}\n\n"
                f"Update:\n{event.update.model_dump_json(indent=2, exclude_none=True)}"
            )

            # Создаем объект файла в памяти
            document_in_memory = BytesIO(error_doc_content.encode('utf-8'))

            # Оборачиваем его в BufferedInputFile
            document_to_send = BufferedInputFile(
                file=document_in_memory.read(),  # Передаем байты
                filename="error_log.txt"
            )

            # Отправляем краткое уведомление
            await bot.send_message(
                chat_id=config.logs_chat,
                text=f"‼️ Произошла ошибка (см. файл). Тип: `{type(event.exception).__name__}`",
                parse_mode="HTML"  # Используем Markdown для `...`
            )
            # Отправляем сам документ
            await bot.send_document(
                chat_id=config.logs_chat,
                document=document_to_send
            )

        else:
            await bot.send_message(
                chat_id=config.logs_chat,
                text=error_message,
                parse_mode='HTML'
            )
    except Exception as e:
        logging.critical(f"Критическая ошибка при попытке отправить лог ошибки. Ошибка: {e}")
        logging.exception(event.exception)
