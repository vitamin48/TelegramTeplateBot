from aiogram.fsm.state import State, StatesGroup


class DateInputStateProductsOrdered(StatesGroup):
    start_date_PO = State()
    end_date_PO = State()
