import sqlite3


def get_start_data():
    """
    Получаем токен, чат для логов и список админов.
    """
    with sqlite3.connect('db_bot.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT TOKEN_BOT FROM TOKENS_BOT")
        token = str(cursor.fetchone()[0])
        cursor.execute("SELECT ADMIN_ID FROM ADMINS_ID")
        admins_lst = [row[0] for row in cursor.fetchall()]
        cursor.execute("SELECT LOGS_CHAT_ID FROM LOGS_CHATS_ID")
        logs_chats_lst = [row[0] for row in cursor.fetchall()]
    return token, admins_lst, logs_chats_lst


TOKEN, ADMINS_ID, LOGS_CHATS_ID = get_start_data()
