import asyncio
import datetime
import logging

from aiogram import types
import random


from db.payment_db import PaymentTable

from keyboards.inline_category import *
from main import bot,dp
from src.utils import generate_label, task_check_payment

user_table = DataBase('database.db')
category_table = CategoryTable('database.db')
product_table = ProductTable('database.db')
server_table = ServerTable('database.db')
basket_table = BasketTable('database.db')
price_table = PriceTable('database.db')
payment_table = PaymentTable('database.db')

logger = logging.getLogger('app.product')

@dp.callback_query_handler(cb_category.filter(action='categories'))
async def category_cb(call:types.CallbackQuery,callback_data:dict):
    logger.info(f'Функция category_cb {call.message.chat.first_name}')
    server_id = callback_data.get('server')
    category_id = callback_data.get('category')

    category_name = await category_table.get_category(category_id=category_id)
    server_name = await server_table.get_server_name(server_id=server_id)

    await call.message.delete()
    await call.message.answer(f'➖➖➖<b>Товар: {category_name} | {server_name}➖➖➖</b>',reply_markup= await product_inline(server_id=server_id,category_id=category_id))


@dp.callback_query_handler(cb_product.filter(action='product'))
async def pay_method_cb(call:types.CallbackQuery,callback_data:dict):
    logger.info(f'Функция pay_method_cb {call.message.chat.first_name}')

    server_id = callback_data.get('server')
    category_id = callback_data.get('category')
    quantity = int(callback_data.get('quantity'))

    user_id = await user_table.get_user(call.message.chat.id)

    available_chooses_products = await product_table.get_active_choose_products(category_id=category_id,
                                                                                server_id=server_id)

    products_id = random.sample(available_chooses_products,quantity)

    label = await generate_label()

    ##Забронировать рандомный аккаунт из активных
    ##И сделать ему резерв

    price_product = await price_table.get_price(server_id=server_id, category_id=category_id)

    order_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

    for product_id in products_id:
        await product_table.reserve_product_for(reserved_id=user_id,
                                                status='reserved',
                                                product_id=product_id[0],
                                                label=label)

    await payment_table.add_pre_payment(label=label,
                                        user_id=user_id,
                                        amount=price_product * quantity,
                                        status='active',
                                        time_stamp=order_time)

    await call.message.edit_text('💳<i>Выберите способ оплаты:</i>',reply_markup=await payments_method(category_id=category_id,
                                                                                                       server_id=server_id,
                                                                                                       quantity=quantity,
                                                                                                       label=label,
                                                                                                       user_id=call.message.chat.id))

    # ТУТ проверяется если до оплаты не дошло
    #asyncio.create_task(task_check_payment(bot=bot,
    #                                       label=label,
    #                                       user_id=user_id,
    #                                       ))
#





