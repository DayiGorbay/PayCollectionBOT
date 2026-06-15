from aiogram.fsm.state import State, StatesGroup


class FreeConnectState(StatesGroup):
    waiting_username = State()
