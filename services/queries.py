import asyncpg
from aiogram.types import User


async def add_user(db: asyncpg.Connection, user: User, referral_source: str = None):
    """
    Добавляет пользователя в БД или обновляет данные, если он уже есть (Upsert).
    """
    sql = """
        INSERT INTO users (telegram_id, username, first_name, last_name, language_code, referral_source)
        VALUES ($1, $2, $3, $4, $5, $6)
        ON CONFLICT (telegram_id) DO UPDATE SET
            username = EXCLUDED.username,
            first_name = EXCLUDED.first_name,
            last_name = EXCLUDED.last_name,
            updated_at = NOW()
        RETURNING id
    """
    # Если referral_source не передан, запишется NULL (или старое значение не перезапишется,
    # но в данном запросе мы вставляем referral_source только при INSERT.
    # При UPDATE рефералка обычно не меняется, так как атрибуция идет по первому входу).

    await db.execute(
        sql,
        user.id,
        user.username,
        user.first_name,
        user.last_name,
        user.language_code,
        referral_source
    )


async def get_lexicon(db: asyncpg.Connection, lex_key: str, lang: str = 'ru') -> str:
    sql = "SELECT text FROM lexicon WHERE lex_key = $1 AND lang_code = $2"
    result = await db.fetchval(sql, lex_key, lang)
    return result or f"Текст для ключа '{lex_key}' не найден."


async def is_admin(db: asyncpg.Connection, telegram_id: int) -> bool:
    sql = "SELECT is_admin FROM users WHERE telegram_id = $1"
    result = await db.fetchval(sql, telegram_id)
    return result or False


async def get_all_active_user_ids(db: asyncpg.Connection) -> list[int]:
    rows = await db.fetch("SELECT telegram_id FROM users WHERE status = 'active'")
    return [row['telegram_id'] for row in rows]


async def deactivate_user(db: asyncpg.Connection, telegram_id: int):
    sql = "UPDATE users SET status = 'inactive' WHERE telegram_id = $1"
    await db.execute(sql, telegram_id)
