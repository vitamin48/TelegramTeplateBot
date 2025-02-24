import sqlite3


class Config:
    def __init__(self, path_to_db='db_bot.db'):
        with sqlite3.connect(path_to_db) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT TOKEN_BOT FROM TOKENS_BOT ORDER BY ROWID ASC")
            tokens = cursor.fetchall()
            self.token = tokens[0][0]
            # self.test_token = tokens[1][0]
            cursor.execute("SELECT ADMIN_ID FROM ADMINS_ID")
            self.admins = [row[0] for row in cursor.fetchall()]
            cursor.execute("SELECT client_id, api_key, Description FROM admins_client_id_api_key")  # Замените `my_table` на вашу таблицу
            self.client_id_api_key = cursor.fetchall()
            # cursor.execute("SELECT LOGS_CHAT_ID FROM LOGS_CHATS_ID ORDER BY ROWID ASC")
            # logs_and_errors_chats = cursor.fetchall()
            # self.logs_chat = logs_and_errors_chats[0][0]
            # self.errors_chat = logs_and_errors_chats[1][0]


config = Config()
print()
