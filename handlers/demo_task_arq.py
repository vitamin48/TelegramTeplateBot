from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from arq.connections import ArqRedis

from services.logger import logger
from services.FSM import ReportState
from services.keyboards import get_confirm_cancel_kb
from services.callbacks import DemoTaskCallback  # <--- Импорт

router = Router()


@router.message(Command("report"))
async def ask_for_report(message: Message, state: FSMContext):
    await message.answer(
        "Вы хотите сгенерировать тяжелый отчет?",
        reply_markup=get_confirm_cancel_kb().as_markup()
    )
    await state.set_state(ReportState.confirm)


# Ловим нажатие, если это DemoTaskCallback И action == "cancel"
@router.callback_query(ReportState.confirm, DemoTaskCallback.filter(F.action == "cancel"))
async def cancel_report(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text("Отменено.")
    await callback.answer()


# Ловим нажатие, если это DemoTaskCallback И action == "confirm"
@router.callback_query(ReportState.confirm, DemoTaskCallback.filter(F.action == "confirm"))
async def queue_report_task(callback: CallbackQuery, state: FSMContext, arq_pool: ArqRedis):
    await state.clear()

    # Редактируем сообщение, чтобы пользователь знал, что его запрос принят
    status_msg = await callback.message.edit_text(
        "✅ Ваш запрос принят. Начинаю работать..."
    )

    # Ставим задачу в очередь Arq
    await arq_pool.enqueue_job(
        "generate_demo_task",
        {"chat_id": callback.message.chat.id, "status_msg_id": status_msg.message_id}
    )
    logger.info(f"Задача generate_demo_task поставлена в очередь для чата {callback.message.chat.id}")
    await callback.answer()
