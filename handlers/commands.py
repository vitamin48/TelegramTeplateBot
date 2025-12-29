import asyncpg
import os
from collections import deque
from aiogram import Router, Bot, F
from aiogram.filters import Command, CommandStart, CommandObject
from aiogram.types import Message, CallbackQuery, BufferedInputFile
from aiogram.utils.keyboard import InlineKeyboardBuilder

from services.logger import logger, log_file
from services.format_message_info import format_message_info, format_callback_query_info
from services.queries import add_user, get_lexicon, is_admin
from services.config import Config

router = Router()


@router.message(CommandStart())
async def start_command(message: Message, bot: Bot, db: asyncpg.Connection, config: Config, command: CommandObject):
    # Извлекаем реферальный аргумент (например, /start google -> args='google')
    referral_source = command.args

    # Регистрируем или обновляем пользователя
    await add_user(db, message.from_user, referral_source)

    logger.info(f"Пользователь {message.from_user.id} отправил /start. Ref: {referral_source}")

    # Отправляем лог в чат логов
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


@router.message(Command(commands=["logs"]))
async def logs_command(
        message: Message,
        command: CommandObject,
        db: asyncpg.Connection
):
    """
    Отправляет файл с последними N строками лога.
    Использование: /logs [количество_строк] (по умолчанию 200)
    """
    # 1. Проверка прав админа
    if not await is_admin(db, message.from_user.id):
        return

    # 2. Определение количества строк
    lines_count = 200
    if command.args:
        try:
            lines_count = int(command.args)
        except ValueError:
            await message.answer("Ошибка: Аргумент должен быть числом. Пример: /logs 500")
            return

    # 3. Чтение файла
    try:
        if not os.path.exists(log_file):
            await message.answer("Файл логов не найден.")
            return

        with open(log_file, "r", encoding="utf-8") as f:
            last_lines = deque(f, maxlen=lines_count)
            logs_content = "".join(last_lines)

        if not logs_content:
            await message.answer("Лог-файл пуст.")
            return

        # 4. Создание и отправка файла
        document = BufferedInputFile(
            file=logs_content.encode("utf-8"),
            filename=f"bot_logs_last_{lines_count}.txt"
        )

        await message.answer_document(
            document=document,
            caption=f"📄 Последние {lines_count} строк лога."
        )
        logger.info(f"Админ {message.from_user.id} выгрузил {lines_count} строк лога.")

    except Exception as e:
        logger.error(f"Ошибка при выгрузке логов: {e}")
        await message.answer(f"Не удалось выгрузить логи: {e}")


@router.message(Command(commands=["send"]))
async def send_command(message: Message, bot: Bot, db: asyncpg.Connection, config: Config):
    # 1. Проверка прав
    if not await is_admin(db, message.from_user.id):
        await bot.send_message(
            chat_id=config.logs_chat,
            text=f'Пользователь {message.from_user.id} ({message.from_user.full_name}) попытался использовать команду /send'
        )
        return

    try:
        # 3. Парсинг команды
        command_parts = message.text.split(' ', 2)
        if len(command_parts) < 3:
            await message.answer("Неверный формат. Используйте: /send <chat_id> <текст>")
            return

        _, chat_id, text = command_parts

        # 4. Кнопки
        keyboard = InlineKeyboardBuilder()
        if '<btn>' in text:
            text, buttons_data = text.split('<btn>', 1)
            buttons = buttons_data.split('<btn>')
            for button in buttons:
                keyboard.button(text=button.strip(),
                                callback_data=f'admin_btn_{button.strip()}')
            keyboard.adjust(1)

        await bot.send_message(chat_id, text, reply_markup=keyboard.as_markup())
        await message.answer(f"Сообщение успешно отправлено в чат {chat_id}.")
        logger.info(f"Админ {message.from_user.id} отправил сообщение в чат {chat_id}")

    except Exception as e:
        logger.error(f"Ошибка при выполнении /send: {e}")
        await message.answer(f"Произошла ошибка: {e}")


# Хэндлер для обработки нажатий на кнопки
@router.callback_query(F.data.startswith("admin_btn_"))
async def button_pressed(callback_query: CallbackQuery, bot: Bot, config: Config):
    await bot.send_message(
        chat_id=config.logs_chat,
        text=format_callback_query_info(callback_query),
        parse_mode='html'
    )
    # Удаляем сообщение с кнопкой у пользователя (или редактируем, чтобы кнопка пропала)
    await bot.delete_message(chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id)
    await callback_query.answer()
