import aiosqlite


class Config:
    """Простой класс-контейнер для хранения конфигурации."""

    def __init__(self, token: str, admins: list[int], logs_chat: int | None = None):
        self.token = token
        self.admins = admins
        self.logs_chat = logs_chat


async def load_config(path_to_db: str = 'db_bot.db') -> Config:
    """
    Асинхронно загружает конфигурацию из базы данных.
    """
    async with aiosqlite.connect(path_to_db) as db:
        # Получаем токен
        async with db.execute("SELECT TOKEN_BOT FROM TOKENS_BOT ORDER BY ROWID ASC LIMIT 1") as cursor:
            token_row = await cursor.fetchone()
            if not token_row:
                raise ValueError("Токен бота не найден в базе данных!")
            token = token_row[0]

        # Получаем список админов
        async with db.execute("SELECT ADMIN_ID FROM ADMINS_ID") as cursor:
            admins = [row[0] for row in await cursor.fetchall()]
            ...

        async with db.execute("SELECT LOGS_CHAT_ID FROM LOGS_CHATS_ID ORDER BY ROWID ASC LIMIT 1") as cursor:
            logs_chat_row = await cursor.fetchone()
            logs_chat = logs_chat_row[0] if logs_chat_row else None

    return Config(token=token, admins=admins, logs_chat=logs_chat)
