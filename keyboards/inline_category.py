from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.callback_data import CallbackData

from db.category_db import CategoryTable
from db.database import DataBase
from db.price_db import PriceTable
from db.product_db import ProductTable
from db.server_db import ServerTable
from db.basket_db import BasketTable

user_table = DataBase('database.db')
category_table = CategoryTable('database.db')
product_table = ProductTable('database.db')
server_table = ServerTable('database.db')
basket_table = BasketTable('database.db')
price_table = PriceTable('database.db')

cb = CallbackData('btn','action')
cb_server = CallbackData('btn', 'action', 'server')
cb_category = CallbackData('btn', 'action', 'category','server')
cb_product = CallbackData('btn','action','category','server','quantity')
cb_payment = CallbackData('btn','action','category','server','quantity','label')

def category_server_inline(servers):
    keyboard = InlineKeyboardMarkup()

    for server in servers:
        server_id = server[0]
        server_name = server[1]

        keyboard.add(InlineKeyboardButton(text=f'🎮  Valorant accounts | {server_name} 🌐', callback_data=cb_server.new(action='servers',
                                                                                               server=server_id)))

    return keyboard

async def category_inline(categories,server):

    keyboard = InlineKeyboardMarkup()

    for category in categories:

        category_id = category[0]
        category_name = category[1]
        count_product = await product_table.get_count_product(server_id=server,category_id=category_id)
        price_product = await price_table.get_price(server_id=server,category_id=category_id)

        if count_product >0:
            keyboard.add(InlineKeyboardButton(text=f'{category_name} | {price_product} rub. |{count_product} шт.',
                                                                callback_data=cb_category.new(action='categories',
                                                                                              category=category_id,
                                                                                              server=server)))
    keyboard.add(InlineKeyboardButton(text='Назад ко всем категориям',callback_data=cb.new(action='back_to_category')))
    return keyboard


async def product_inline(server_id, category_id):
    keyboard = InlineKeyboardMarkup()

    count_product = await product_table.get_count_product(server_id, category_id)
    counter = 10 if count_product >= 10 else count_product

    row_buttons = []

    for count in range(1, count_product + 1):
        button = InlineKeyboardButton(text=str(count), callback_data=cb_product.new(action='product',
                                                                                    category=category_id,
                                                                                    server=server_id,
                                                                                    quantity=count))
        row_buttons.append(button)

        counter -= 1
        if counter == 0 or count % 5 == 0:
            keyboard.row(*row_buttons)
            row_buttons = []

        if counter == 0:
            break
    keyboard.add(InlineKeyboardButton(text='Назад',callback_data=cb_category.new(action='back',
                                                                                 category=category_id,
                                                                                 server=server_id)))
    return keyboard


async def payments_method(category_id,server_id,quantity,label,user_id):
    keyboard = InlineKeyboardMarkup()

    balance = await user_table.get_balance(user_id)

    keyboard.add(InlineKeyboardButton(text='CryptoBot',callback_data=cb_payment.new(action='CryptoBot',
                                                                                    category=category_id,
                                                                                    server=server_id,
                                                                                    quantity=quantity,
                                                                                    label=label)))
    keyboard.add(InlineKeyboardButton(text='YooMoney(Карта/Кошелек)', callback_data=cb_payment.new(action='YooMoney',
                                                                                                   category=category_id,
                                                                                                   server=server_id,
                                                                                                   quantity=quantity,
                                                                                                   label=label)))
    #keyboard.add(InlineKeyboardButton(text='Lolz', callback_data=cb_payment.new(action='lolz',
    #                                                                                  category=category_id,
    #                                                                                  server=server_id,
    #                                                                                  quantity=quantity,
    #                                                                                  label=label)))
    if balance >0:
        keyboard.add(InlineKeyboardButton(text='Balance',callback_data=cb_payment.new(action='Balance',
                                                                                      category=category_id,
                                                                                      server=server_id,
                                                                                      quantity=quantity,
                                                                                      label=label)))
    return keyboard


async def payment_menu(category_id,server_id,quantity,label,url,flag:str):

    keyboard = InlineKeyboardMarkup()
    # https://t.me/CryptoTestnetBot
    # https://t.me/CryptoBot
    if flag == 'CryptoBot':
        url = f'https://t.me/CryptoBot?start={url}'
        keyboard.add(InlineKeyboardButton(text='Перейти к оплате',url=url))
    else:
        keyboard.add(InlineKeyboardButton(text='Перейти к оплате',url=url))
    keyboard.add(InlineKeyboardButton(text='Отмена',callback_data=cb_payment.new(action='cancel_pay',
                                                                                 category=category_id,
                                                                                 server=server_id,
                                                                                 quantity=quantity,
                                                                                 label=label)))
    return keyboard


async def pay_balance(category_id,server_id,quantity,label):

    keyboard = InlineKeyboardMarkup()

    keyboard.add(InlineKeyboardButton(text='Оплатить', callback_data=cb_payment.new(action='pay_balance',
                                                                                    category=category_id,
                                                                                    server=server_id,
                                                                                    quantity=quantity,
                                                                                    label=label)))

    return keyboard


##Сделать через флаг клавиатуру общую
#async def payment_menu_cryptobot(category_id,server_id,quantity,url_prefix,label):
#    url= f'https://t.me/CryptoTestnetBot?start={url_prefix}'
#
#    keyboard = InlineKeyboardMarkup()
#
#    keyboard.add(InlineKeyboardButton(text='Перейти к оплате',url=url))
#    return keyboard


#async def payment_menu_crystalpay(category_id,server_id,quantity,url,label):
#
#    keyboard = InlineKeyboardMarkup()
#
#    keyboard.add(InlineKeyboardButton(text='Перейти к оплате',url=url))
#    #keyboard.add(InlineKeyboardButton(text='Проверить оплату',callback_data=cb_payment.new(
#    #    action='check_payment_yoomoney',category=category_id,server=server_id,quantity=quantity,label=label
#    #)))
#    #keyboard.add(InlineKeyboardButton(text='Отменить',callback_data=cb_payment.new(
#    #    action='cancel_payment_yoomoney',category=category_id,server=server_id,quantity=quantity,label=label
#    #)))
#
#    return keyboard