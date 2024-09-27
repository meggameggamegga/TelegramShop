import logging

from aiogram.dispatcher.filters import Command
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import ContentType
from aiogram.utils.markdown import hlink

import config
from db.category_db import CategoryTable
from db.payment_db import PaymentTable
from db.product_db import ProductTable
from db.server_db import ServerTable
from db.basket_db import BasketTable
from keyboards.inline_category import category_server_inline, cb, cb_payment
from main import bot,dp
from db.database import DataBase
from keyboards.menu_start import menu_kb

user_table = DataBase('database.db')
category_table = CategoryTable('database.db')
product_table = ProductTable('database.db')
server_table = ServerTable('database.db')
basket_table = BasketTable('database.db')
payment_table = PaymentTable('database.db')

logger = logging.getLogger('app.base')

@dp.message_handler(Command('start'))
async def start_cmnd(message: types.Message):
    logger.info(f'Функция start_cmnd {message.from_user.first_name}')
    user_exist = await user_table.user_exist(message.from_user.id)
    if not user_exist:
        if int(message.from_user.id) != int(config.ADMIN_ID):
            await bot.send_message(config.ADMIN_ID, f'Пользватель {message.from_user.first_name}')
        await user_table.add_user(message.from_user.id,message.from_user.first_name)



    await message.answer(config.START_MESSAGE, reply_markup=menu_kb())



@dp.message_handler(text=config.CATEGORY_BTN,content_types=ContentType.TEXT)
async def category_cmnd(message:types.Message):
    logger.info(f'Функция category_cmnd {message.from_user.first_name}')
    servers = await server_table.get_all_servers()

    await message.answer('<i>Категории:</i>',reply_markup=category_server_inline(servers))

@dp.callback_query_handler(cb.filter(action='back_to_category'))
async def category_cb_cmnd(call:types.CallbackQuery):
    logger.info(f'Функция category_cb_cmnd {call.message.chat.first_name}')
    servers = await server_table.get_all_servers()

    await call.message.delete()
    await call.message.answer('<i>Категории:</i>',reply_markup=category_server_inline(servers))


@dp.callback_query_handler(cb_payment.filter(action='cancel_pay'))
async def cancel_payment(call:types.CallbackQuery,callback_data:dict):
    logger.info(f'Функция cancel_payment {call.message.chat.first_name}')
    label = callback_data.get('label')


    try:
        await product_table.unreserved_product(status='available', label=label)
    except Exception as e:
        print('Ошибка в отмене об оплате',e)

    await payment_table.change_status_payment(status='canceled',label=label)

    await call.message.delete()
    await call.answer('Оплата отменена')
    await call.message.answer(f'<b>Заказ <i><code>#{label}</code></i> отменен</b>')



@dp.message_handler(text=config.AMOUNT_BTN, content_types=ContentType.TEXT)
async def amount_cmnd(message: types.Message):
    logger.info(f'Функция amount_cmnd {message.from_user.first_name}')
    text = '<b>Товары</b>\n\n'
    categories = await user_table.get_server_categories_with_products_and_prices()
    for category in categories:
        server_id, server_name, category_id, category_name, product_count, total_price = category
        if category_name is None:
            continue
        if not text or f"➖➖➖➖➖➖ Valorant {server_name}➖➖➖➖➖➖" not in text:
            text += f"\n\n➖➖➖➖➖➖ Valorant {server_name}➖➖➖➖➖➖\n\n"



        text += f"{category_name}| {product_count} шт.\n"

    await message.answer(text)


@dp.message_handler(text=config.SUPPORT_BTN, content_types=ContentType.TEXT)
async def support_cmnd(message: types.Message):
    logger.info(f'Функция support_cmnd {message.from_user.first_name}')
    await message.answer('По всем вопросам')

@dp.message_handler(text=config.RULES_BTN, content_types=ContentType.TEXT)
async def rules_cmnd(message: types.Message):
    logger.info(f'Функция rules_cmnd {message.from_user.first_name}')
    await message.answer(config.RULES_MESSAGE)