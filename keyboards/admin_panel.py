from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.callback_data import CallbackData

from db.category_db import CategoryTable
from db.price_db import PriceTable
from db.product_db import ProductTable
from db.server_db import ServerTable
from db.basket_db import BasketTable


category_table = CategoryTable('database.db')
product_table = ProductTable('database.db')
server_table = ServerTable('database.db')
basket_table = BasketTable('database.db')
price_table = PriceTable('database.db')


cb_admin = CallbackData('btn','action')
cb_admin_payment = CallbackData('btn','action','page')
cb_admin_send_message = CallbackData('btn','action','text')

async def admin_menu():
    keyboard = InlineKeyboardMarkup()

    keyboard.add(
        InlineKeyboardButton(text='Добавить аккаунты 🛍️', callback_data=cb_admin.new(action='add_accounts')),
        InlineKeyboardButton(text='Изменить баланс юзера 💰', callback_data=cb_admin.new(action='change_balance'))
    )

    keyboard.add(
        InlineKeyboardButton(text='Кол-во пользователей 👥', callback_data=cb_admin.new(action='send_users')),
        InlineKeyboardButton(text='Отобразить категорию и цену 📊', callback_data=cb_admin.new(action='category_price'))
    )

    keyboard.add(
        InlineKeyboardButton(text='Оплаченые платежи 💳', callback_data=cb_admin.new(action='paid_payments'))
    )

    keyboard.add(
        InlineKeyboardButton(text='Сделать рассылку',callback_data=cb_admin.new(action='send_message'))
    )


    return keyboard

async def send_message_kb(text):
    keyboard = InlineKeyboardMarkup()

    keyboard.add(InlineKeyboardButton(text='Да',callback_data=cb_admin_send_message.new(action='send_message_yes',
                                                                                        text=text)))
    keyboard.add(InlineKeyboardButton(text='Отмена',callback_data=cb_admin.new(action='back')))

    return keyboard
async def admin_cancel():
    keyboard = InlineKeyboardMarkup()

    keyboard.add(InlineKeyboardButton(text='Отмена',callback_data=cb_admin.new(action='cancel_admin')))

    return keyboard


async def payment_keyboard(page):
    keyboard = InlineKeyboardMarkup()

    keyboard.row(InlineKeyboardButton(text='<-',callback_data=cb_admin_payment.new(action='paid_keyboard',
                                                                                   page=page-1)),
                 InlineKeyboardButton(text='->',callback_data=cb_admin_payment.new(action='paid_keyboard',
                                                                                   page=page+1)))
    keyboard.add(InlineKeyboardButton(text='Назад',callback_data=cb_admin.new(action='back')))
    return keyboard

async def back_keyboard():
    keyboard = InlineKeyboardMarkup()

    keyboard.add(InlineKeyboardButton(text='Назад',callback_data=cb_admin.new(action='back')))

    return keyboard
