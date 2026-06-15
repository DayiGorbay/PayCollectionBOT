from aiogram.fsm.state import State, StatesGroup


class ShopState(StatesGroup):
    waiting_username = State()
    waiting_topup_amount = State()
    waiting_receipt = State()
    waiting_discount_code = State()
