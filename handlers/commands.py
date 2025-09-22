import aiosqlite  # Импортируем aiosqlite
from aiogram import Router, Bot
from aiogram.filters import Command, CommandStart
from aiogram.types import Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram import F

from services.logger import logger
from utils.format_message_info import format_message_info, format_callback_query_info
from services.queries import add_user, get_lexicon
from services.config import Config

send_command = Router()


# Обработчик команды /start
@send_command.message(CommandStart())
async def start_command(message: Message, bot: Bot, db: aiosqlite.Connection, config: Config):
    # Вызываем асинхронные функции
    await add_user(db, message)
    log_text = f"Пользователь {message.from_user.id} отправил команду /start"
    logger.info(log_text)
    await bot.send_message(chat_id=config.logs_chat, text=format_message_info(message),
                           parse_mode='html')

    lexicon_text = await get_lexicon(db, message.from_user.language_code, 'start')
    await message.answer(text=lexicon_text or "Добро пожаловать!")


# Обработчик команды /send
@send_command.message(Command(commands=["send"]))
async def send_message(message: Message, bot: Bot, config: Config):
    # Получаем объект config
    user_id = message.from_user.id
    if user_id in config.admins:
        try:
            command_parts = message.text.split(' ', 2)
            if len(command_parts) < 3:
                await message.answer("Неправильный формат команды. Используйте: /send <chat_id> <текст>")
                return
            chat_id = command_parts[1]
            text = command_parts[2]
            keyboard = InlineKeyboardBuilder()
            if '<btn>' in text:
                text, buttons = text.split('<btn>', 1)
                buttons = buttons.split('<btn>')
                for button in buttons:
                    keyboard.button(text=button, callback_data=f'btn_{button}')
                keyboard.adjust(1)
            await bot.send_message(chat_id, text, reply_markup=keyboard.as_markup())
            await message.answer(f"Сообщение отправлено в чат ID {chat_id}: {text}")
            logger.info(f"Сообщение отправлено в чат ID {chat_id} от пользователя {message.from_user.id}: {text}")
        except Exception as exp:
            logger.error(f"Ошибка при отправке сообщения: {exp}")
            await message.answer(f"Произошла ошибка при отправке сообщения: {exp}")
    else:
        await bot.send_message(chat_id=config.logs_chat, text='Кто-то не из админов отправил команду /send',
                               parse_mode='html')


# Хэндлер для обработки нажатий на кнопки
@send_command.callback_query(F.data.startswith("btn_"))
async def button_pressed(callback_query: CallbackQuery, bot: Bot, config: Config):
    button_text = callback_query.data.split("_", 1)[1]
    await bot.send_message(chat_id=config.logs_chat, text=format_callback_query_info(callback_query),
                           parse_mode='html')
    await bot.delete_message(chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id)
