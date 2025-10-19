import os
from dotenv import load_dotenv
from urllib.parse import quote_plus
from dataclasses import dataclass

load_dotenv()


@dataclass
class Config:
    token: str
    logs_chat: int
    redis_host: str
    redis_port: int


def load_config() -> Config:
    return Config(
        token=os.getenv("BOT_TOKEN"),
        logs_chat=int(os.getenv("LOGS_CHAT_ID")),
        redis_host=os.getenv("REDIS_HOST", "localhost"),
        redis_port=int(os.getenv("REDIS_PORT", 6379))
    )


DB_HOST = os.getenv("PG_HOST", "localhost")
DB_PORT = int(os.getenv("PG_PORT", 5432))
DB_USER = os.getenv("PG_USER")
DB_PASS = os.getenv("PG_PASSWORD")
DB_NAME = os.getenv("PG_DATABASE")

encoded_pass = quote_plus(DB_PASS) if DB_PASS else ""
DATABASE_URL = f"postgresql://{DB_USER}:{encoded_pass}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
