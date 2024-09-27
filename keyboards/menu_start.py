from aiogram.types import KeyboardButton,ReplyKeyboardMarkup

import config
def menu_kb():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)

    keyboard.row(KeyboardButton(text=config.CATEGORY_BTN), KeyboardButton(text=config.AMOUNT_BTN))
    keyboard.row(KeyboardButton(text=config.RULES_BTN), KeyboardButton(text=config.SUPPORT_BTN))
    keyboard.add(KeyboardButton(text=config.PROFILE_BTN))

    return keyboard
