from aiogram.dispatcher.filters.state import StatesGroup, State


class getLabel(StatesGroup):
    label = State()