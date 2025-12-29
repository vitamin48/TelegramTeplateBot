import asyncpg
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from services.queries import get_lexicon

router = Router()


@router.message(Command(commands=["help"]))
async def help_command(message: Message, db: asyncpg.Connection):
    # Получаем текст справки из БД (таблица lexicon)
    lexicon_text = await get_lexicon(db, 'help')
    await message.answer(text=lexicon_text)
