import asyncpg
from aiogram import Router, Bot
from aiogram.filters import Command, CommandStart
from aiogram.types import Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder

from services.logger import logger
from services.format_message_info import format_message_info
from services.queries import add_user, get_lexicon, is_admin
from services.config import Config

router = Router()


@router.message(CommandStart())
async def start_command(message: Message, bot: Bot, db: asyncpg.Connection, config: Config):
    await add_user(db, message.from_user)
    logger.info(f"Пользователь {message.from_user.id} отправил /start")
    await bot.send_message(
        chat_id=config.logs_chat,
        text=format_message_info(message)
    )
    lexicon_text = await get_lexicon(db, 'start')
    await message.answer(text=lexicon_text)


@router.message(Command(commands=["help"]))
async def help_command(message: Message, db: asyncpg.Connection):
    lexicon_text = await get_lexicon(db, 'help')
    await message.answer(text=lexicon_text)


@router.message(Command(commands=["send"]))
async def send_command(message: Message, bot: Bot, db: asyncpg.Connection, config: Config):
    # 1. Проверка прав из Варианта 1 (гибкость)
    if not await is_admin(db, message.from_user.id):
        # 2. Уведомление в лог-чат из Варианта 2 (безопасность)
        await bot.send_message(
            chat_id=config.tg_bot.logs_chat,
            text=f'Пользователь {message.from_user.id} ({message.from_user.full_name}) попытался использовать команду /send'
        )
        # await message.answer("У вас нет прав для выполнения этой команды.")
        return

    try:
        # 3. Надежный парсинг из Варианта 2
        command_parts = message.text.split(' ', 2)
        if len(command_parts) < 3:
            await message.answer("Неверный формат. Используйте: /send <chat_id> <текст>")
            return

        _, chat_id, text = command_parts

        # 4. Функциональность с кнопками из Варианта 2
        keyboard = InlineKeyboardBuilder()
        if '<btn>' in text:
            text, buttons_data = text.split('<btn>', 1)
            buttons = buttons_data.split('<btn>')
            for button in buttons:
                keyboard.button(text=button.strip(),
                                callback_data=f'admin_btn_{button.strip()}')  # callback_data лучше делать уникальными
            keyboard.adjust(1)

        await bot.send_message(chat_id, text, reply_markup=keyboard.as_markup())
        await message.answer(f"Сообщение успешно отправлено в чат {chat_id}.")
        logger.info(f"Админ {message.from_user.id} отправил сообщение в чат {chat_id}")

    except Exception as e:
        logger.error(f"Ошибка при выполнении /send: {e}")
        await message.answer(f"Произошла ошибка: {e}")


# Хэндлер для обработки нажатий на кнопки
@send_command.callback_query(F.data.startswith("btn_"))
async def button_pressed(callback_query: CallbackQuery, bot: Bot, config: Config):
    button_text = callback_query.data.split("_", 1)[1]
    await bot.send_message(chat_id=config.logs_chat, text=format_callback_query_info(callback_query),
                           parse_mode='html')
    await bot.delete_message(chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id)
