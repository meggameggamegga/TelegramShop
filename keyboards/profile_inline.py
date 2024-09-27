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

cb_profile_back = CallbackData('btn','action')
cb_profile = CallbackData('btn','action','user_id')
cb_profile_pagination = CallbackData('btn','action','user_id','page')
cb_profile_send_order = CallbackData('btn','action','label')
cb_profile_get_change = CallbackData('btn','action')

async def profile_menu(user_id):
    keyboard = InlineKeyboardMarkup()

   #keyboard.add(InlineKeyboardButton(text='История заказов', callback_data=cb_profile.new(action='orders_history',
   #                                                                                       user_id=user_id)))
    keyboard.add(InlineKeyboardButton(text='Менеджер заказов/пополнений',callback_data=cb_profile.new(action='payment_history',
                                                                                                      user_id=user_id)))
    keyboard.add(InlineKeyboardButton(text='Получить замену',callback_data=cb_profile_get_change.new(action='get_replace')))

    return keyboard

async def profile_back():
    keyboard = InlineKeyboardMarkup()

    keyboard.add(InlineKeyboardButton(text='Назад', callback_data=cb_profile_back.new(action='back')))

    return keyboard


async def pagination_menu_payments(start_index,user_id_table,end_index,total_payments,page,labels):
    keyboard = InlineKeyboardMarkup(row_width=2)#Будет по две кнопки , остальные уйдут ниже


    #Тут брать label и выводить по label его заказы
    if start_index == 0 and total_payments > 5:
        # Если находимся на первой странице и есть следующие страницы, то добавляем только стрелку вперед
        keyboard.add(InlineKeyboardButton(text='▶', callback_data=cb_profile_pagination.new(
            action='pagination_payments', user_id=user_id_table, page=page + 1)))
#
    elif start_index > 0 and end_index + 1 < total_payments:
        # Если находимся не на первой странице и есть как предыдущие, так и следующие страницы, то добавляем обе стрелки
        keyboard.row(
            InlineKeyboardButton(text='◀', callback_data=cb_profile_pagination.new(
                action='pagination_payments', user_id=user_id_table, page=page - 1)),
            InlineKeyboardButton(text='▶', callback_data=cb_profile_pagination.new(
                action='pagination_payments', user_id=user_id_table, page=page + 1)))
#
    elif end_index + 1 >= total_payments > 5:
        # Если следующей страницы нет, но есть предыдущая, то добавляем только стрелку назад
        keyboard.add(InlineKeyboardButton(text='◀', callback_data=cb_profile_pagination.new(
            action='pagination_payments', user_id=user_id_table, page=page - 1)))

    #Просто выкидывать ему txt с аккаунтами
    buttons = []
    for label in labels:
        buttons.append(InlineKeyboardButton(text=f'Управление заказом: #{label}',
                                            callback_data=cb_profile_send_order.new(action='send_order',
                                                                                    label=label)))
    keyboard.add(*buttons)


    keyboard.add(InlineKeyboardButton(text='Назад', callback_data=cb_profile_back.new(action='back')))
    return keyboard

async def pagination_menu_orders(start_index,user_id_table,end_index,total_payments,page,
                                 payment_id=None,products_ids=None,user_id=None):

    keyboard = InlineKeyboardMarkup()

    if start_index == 0 and total_payments > 5:
        # Если находимся на первой странице и есть следующие страницы, то добавляем только стрелку вперед
        keyboard.add(InlineKeyboardButton(text='▶', callback_data=cb_profile_pagination.new(
            action='pagination_orders', user_id=user_id_table, page=page + 1)))

    elif start_index > 0 and end_index + 1 < total_payments:
        # Если находимся не на первой странице и есть как предыдущие, так и следующие страницы, то добавляем обе стрелки
        keyboard.row(
            InlineKeyboardButton(text='◀', callback_data=cb_profile_pagination.new(
                action='pagination_orders', user_id=user_id_table, page=page - 1)),
            InlineKeyboardButton(text='▶', callback_data=cb_profile_pagination.new(
                action='pagination_orders', user_id=user_id_table, page=page + 1)))

    elif end_index + 1 >= total_payments > 5:
        # Если следующей страницы нет, но есть предыдущая, то добавляем только стрелку назад
        keyboard.add(InlineKeyboardButton(text='◀', callback_data=cb_profile_pagination.new(
            action='pagination_orders', user_id=user_id_table, page=page - 1)))









    keyboard.add(InlineKeyboardButton(text='Назад', callback_data=cb_profile_back.new(action='back')))

    return keyboard

async def send_order_profile(label):
    keyboard = InlineKeyboardMarkup()

    keyboard.add(InlineKeyboardButton(text='Выслать файл', callback_data=cb_profile_send_order.new(action='send_order_file',
                                                                                                   label=label)))
    keyboard.add(InlineKeyboardButton(text='Назад', callback_data=cb_profile_back.new(action='back')))
    return keyboard
