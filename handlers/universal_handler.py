from aiogram.types import Message
from aiogram import Router, Bot

from utils.format_message_info import format_message_info
from services.config import Config

unihandler = Router()


# Универсальный обработчик сообщений
@unihandler.message()
async def handle_all_messages(message: Message, bot: Bot, config: Config):
    if message.chat.id == config.logs_chat:
        return

    await bot.send_message(chat_id=config.logs_chat, text=format_message_info(message),
                           parse_mode='html')
    await bot.forward_message(chat_id=config.logs_chat, message_id=message.message_id, from_chat_id=message.chat.id)
