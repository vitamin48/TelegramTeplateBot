import asyncio
from aiogram import Router, Bot, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.exceptions import TelegramForbiddenError, TelegramBadRequest

from services.FSM import BroadcastState
from services.queries import get_all_user_ids
from services.logger import logger
from services.config import Config

# Создаем новый роутер для хэндлеров рассылки
router = Router()


def get_confirm_broadcast_kb() -> InlineKeyboardBuilder:
    """Возвращает клавиатуру для подтверждения рассылки."""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="✅ Отправить", callback_data="confirm_send"),
        InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_send")
    )
    return builder


# --- ХЭНДЛЕРЫ ДЛЯ FSM ---

# 1. Хэндлер на команду /broadcast (вход в машину состояний)
@router.message(Command("broadcast"))
async def start_broadcast(message: Message, state: FSMContext, bot: Bot, config: Config):
    if message.from_user.id not in config.admins:
        await message.answer("У вас нет прав для выполнения этой команды.")
        return

    await message.answer("Пришлите сообщение, которое нужно разослать пользователям. "
                         "Вы можете использовать форматирование, фото, видео и кнопки.")
    await state.set_state(BroadcastState.get_content)


# 2. Хэндлер для получения контента и запроса подтверждения
@router.message(BroadcastState.get_content)
async def get_broadcast_content(message: Message, state: FSMContext, bot: Bot, db):
    # Сохраняем ID сообщения, которое будем копировать
    await state.update_data(message_to_copy_id=message.message_id)

    user_ids = await get_all_user_ids(db)
    user_count = len(user_ids)

    # Пересылаем сообщение админу для предпросмотра
    await message.send_copy(
        chat_id=message.from_user.id,
        reply_markup=get_confirm_broadcast_kb().as_markup()
    )
    await message.answer(
        f"Вы собираетесь разослать это сообщение для {user_count} пользователей. Подтвердите отправку.")
    await state.set_state(BroadcastState.confirm_broadcast)


# 3. Хэндлер для отмены рассылки
@router.callback_query(F.data == "cancel_send", BroadcastState.confirm_broadcast)
async def cancel_broadcast(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text("Рассылка отменена.")
    await callback.answer()


# 4. Хэндлер для подтверждения и запуска рассылки
@router.callback_query(F.data == "confirm_send", BroadcastState.confirm_broadcast)
async def confirm_and_start_broadcast(callback: CallbackQuery, state: FSMContext, bot: Bot, db):
    await callback.answer("Начинаю рассылку...")

    data = await state.get_data()
    message_to_copy_id = data.get('message_to_copy_id')
    admin_chat_id = callback.from_user.id

    await state.clear()

    if not message_to_copy_id:
        await bot.send_message(admin_chat_id, "Не удалось найти сообщение для рассылки. Попробуйте снова.")
        return

    user_ids = await get_all_user_ids(db)
    success_count = 0
    fail_count = 0

    logger.info(f"Начинается рассылка для {len(user_ids)} пользователей.")

    for user_id in user_ids:
        try:
            # Используем copy_message для точного копирования сообщения со всеми медиа и кнопками
            await bot.copy_message(
                chat_id=user_id,
                from_chat_id=admin_chat_id,
                message_id=message_to_copy_id
            )
            success_count += 1
            logger.info(f"Сообщение успешно отправлено пользователю {user_id}")
            # ВАЖНО: небольшая задержка, чтобы не попасть под лимиты Telegram
            await asyncio.sleep(0.5)  # 10 сообщений в секунду
        except TelegramForbiddenError:
            logger.warning(f"Не удалось отправить сообщение пользователю {user_id}: бот заблокирован.")
            fail_count += 1
        except Exception as e:
            logger.error(f"Ошибка при отправке сообщения пользователю {user_id}: {e}")
            fail_count += 1

    summary_text = (
        f"✅ Рассылка завершена!\n\n"
        f"Успешно отправлено: {success_count}\n"
        f"Не удалось доставить: {fail_count}"
    )
    await bot.send_message(admin_chat_id, summary_text)
    logger.info(summary_text)
