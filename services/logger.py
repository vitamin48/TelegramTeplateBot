import logging
import os
from colorlog import ColoredFormatter  # Импортируем ColoredFormatter

# Определяем путь к файлу лога в корневой директории проекта
log_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "bot.log")

# Настройка логирования
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Форматтер для файла (без цветов)
file_formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

# Форматтер для консоли (с цветами)
console_formatter = ColoredFormatter(
    "%(log_color)s%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt=None,
    reset=True,
    log_colors={
        'DEBUG': 'purple',
        'INFO': 'cyan',
        'WARNING': 'yellow',
        'ERROR': 'red',
        'CRITICAL': 'red,bg_white',
    },
    secondary_log_colors={},
    style='%'
)

# Обработчик для записи в файл
file_handler = logging.FileHandler(log_file, encoding="utf-8")
file_handler.setFormatter(file_formatter)

# Обработчик для вывода в консоль
console_handler = logging.StreamHandler()
console_handler.setFormatter(console_formatter)

# Добавляем оба обработчика к логгеру
logger.addHandler(file_handler)
logger.addHandler(console_handler)

# # Пример использования
# logger.debug("Это debug сообщение")
# logger.info("Это info сообщение")
# logger.warning("Это warning сообщение")
# logger.error("Это error сообщение")
# logger.critical("Это critical сообщение")
