from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from services.callbacks import DemoTaskCallback  # <--- Импортируем наш класс


def get_confirm_cancel_kb() -> InlineKeyboardBuilder:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text="✅ Подтвердить",
            # .pack() превращает объект в строку "demo:confirm"
            callback_data=DemoTaskCallback(action="confirm").pack()
        ),
        InlineKeyboardButton(
            text="❌ Отмена",
            # .pack() превращает объект в строку "demo:cancel"
            callback_data=DemoTaskCallback(action="cancel").pack()
        )
    )
    return builder


def phone_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Отправить номер телефона", request_contact=True)]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )
