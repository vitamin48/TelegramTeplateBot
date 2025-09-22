import aiosqlite
from datetime import datetime
from aiogram.types import Message

# Константа с именем БД остается
NAME_DB = 'db_bot.db'


async def add_user(db: aiosqlite.Connection, message: Message):
    """
    Добавляет нового пользователя в базу данных асинхронно.
    Принимает объект соединения 'db' из middleware.
    """
    user = message.from_user
    date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # Используем параметризованный запрос для безопасности
    await db.execute(
        '''INSERT OR IGNORE INTO users (date_start, user_id, username, first_name, last_name, language_code)
           VALUES (?, ?, ?, ?, ?, ?)''',
        (date, user.id, user.username, user.first_name, user.last_name, user.language_code)
    )
    # Сохраняем изменения
    await db.commit()


async def get_lexicon(db: aiosqlite.Connection, language_code: str, lex_key: str) -> str | None:
    """
    Получаем текстовое сообщение асинхронно.
    Принимает объект соединения 'db' и код языка.
    """
    # Определяем таблицу на основе кода языка
    table_map = {'ru': 'lexicon_ru', 'uk': 'lexicon_ua'}
    table_name = table_map.get(language_code, 'lexicon_en')  # 'lexicon_en' как значение по умолчанию

    # Выполняем запрос и получаем результат
    async with db.execute(f"SELECT text FROM {table_name} WHERE key = ?", (lex_key,)) as cursor:
        result = await cursor.fetchone()
        if result:
            return str(result[0])
        else:
            # Лучше возвращать None, если ключ не найден
            return None


async def get_all_user_ids(db: aiosqlite.Connection) -> list[int]:
    """
    Возвращает список всех user_id из таблицы users.
    """
    async with db.execute("SELECT user_id FROM users") as cursor:
        # fetchall() вернет список кортежей [(id1,), (id2,), ...],
        # поэтому мы извлекаем первый элемент из каждого кортежа.
        return [row[0] for row in await cursor.fetchall()]
