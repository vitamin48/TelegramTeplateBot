from aiogram.types import Message
from aiogram import Router, Bot
from services.format_message_info import format_message_info
from services.config import Config

unihandler = Router()


@unihandler.message()
async def handle_all_messages(message: Message, bot: Bot, config: Config):
    if message.chat.id == config.logs_chat:
        return
    await bot.send_message(chat_id=config.logs_chat, text=format_message_info(message))
    await bot.forward_message(chat_id=config.logs_chat, from_chat_id=message.chat.id, message_id=message.message_id)
