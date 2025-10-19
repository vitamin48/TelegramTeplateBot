import logging
import traceback
import html
from io import BytesIO
from aiogram import Router, F, Bot
from aiogram.types import ErrorEvent, BufferedInputFile
from services.config import Config

errors_router = Router()


@errors_router.error(F.exception)
async def handle_all_errors(event: ErrorEvent, bot: Bot, config: Config):
    if not config.logs_chat:
        logging.exception(event.exception)
        return

    error_message = (
        f"‼️ <b>Произошла ошибка!</b>\n\n"
        f"<b>Тип:</b> {html.escape(type(event.exception).__name__)}\n"
        f"<b>Ошибка:</b>\n<pre>{html.escape(str(event.exception))}</pre>\n\n"
        f"<b>Update:</b>\n<pre>{html.escape(event.update.model_dump_json(indent=2, exclude_none=True))}</pre>"
    )

    try:
        if len(error_message) > 4096:
            traceback_text = f"Traceback:\n{traceback.format_exc()}"
            document = BufferedInputFile(
                (error_message + "\n\n" + traceback_text).encode('utf-8'),
                filename="error_log.txt"
            )
            await bot.send_document(
                chat_id=config.logs_chat,
                document=document,
                caption=f"‼️ Ошибка (подробности в файле). Тип: `{type(event.exception).__name__}`"
            )
        else:
            await bot.send_message(
                chat_id=config.logs_chat,
                text=error_message,
                parse_mode='HTML'
            )
    except Exception as e:
        logging.critical(f"Критическая ошибка при отправке лога ошибки: {e}")
        logging.exception(event.exception)
