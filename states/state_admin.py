from aiogram.dispatcher.filters.state import StatesGroup, State


class AddAccounts(StatesGroup):
    choose_category = State()
    choose_server = State()
    send_file = State()

class AddCategory(StatesGroup):
    send_category = State()

class AddBalance(StatesGroup):
    send_user_id = State()
    send_balance = State()


class SendMessage(StatesGroup):
    send_message = State()