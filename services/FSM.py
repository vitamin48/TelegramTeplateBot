from aiogram.fsm.state import State, StatesGroup


class BroadcastState(StatesGroup):
    get_content = State()
    confirm_broadcast = State()


class ReportState(StatesGroup):
    confirm = State()
