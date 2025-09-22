from aiogram.fsm.state import State, StatesGroup


class DateInputStateProductsOrdered(StatesGroup):
    start_date_PO = State()
    end_date_PO = State()


class BroadcastState(StatesGroup):
    get_content = State()  # Состояние ожидания контента для рассылки
    confirm_broadcast = State()  # Состояние ожидания подтверждения
