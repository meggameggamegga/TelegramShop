import asyncio
import datetime
import logging


from aiogram import types

import config
from db.database import DataBase
from db.payment_db import PaymentTable
from keyboards.inline_category import *
from main import dp, bot


user_table = DataBase('database.db')
category_table = CategoryTable('database.db')
product_table = ProductTable('database.db')
server_table = ServerTable('database.db')
basket_table = BasketTable('database.db')
price_table = PriceTable('database.db')
payment_table = PaymentTable('database.db')

logger = logging.getLogger('app.payment_balance')

@dp.callback_query_handler(cb_payment.filter(action='Balance'))
async def product_cb(call: types.CallbackQuery, callback_data: dict):
    # Проверить если баланса хватает
    logger.info(f'Функция product_cb (Balance) {call.message.chat.first_name}')

    pay_method = callback_data.get('action')
    server_id = callback_data.get('server')
    category_id = callback_data.get('category')
    quantity = int(callback_data.get('quantity'))
    label = callback_data.get('label')

    balance = await user_table.get_balance(call.message.chat.id)
    category_name = await category_table.get_category(category_id=category_id)
    server_name = await server_table.get_server_name(server_id=server_id)
    price_product = await price_table.get_price(server_id=server_id, category_id=category_id)

    if balance < price_product*quantity:
        await call.answer('Недостаточно баланса')
    else:
        order_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

        PRE_PAYMENT_MESSAGE = f'➖➖➖➖➖➖➖➖➖➖➖➖\n' \
                              f'📃<b>Товар:</b> {category_name} | {server_name}\n' \
                              f'💰<b>Цена:</b> {price_product}\n' \
                              f'📦<b>Кол-во:</b> {quantity}\n' \
                              f'💡<b>Заказ:</b> <i><code>#{label}</code></i>\n' \
                              f'🕐<b>Время заказа:</b> {order_time}\n' \
                              f'💲<b>Итоговая сумма:</b> {price_product * quantity} руб.\n' \
                              f'💲<b>Способ оплаты:</b> {pay_method}\n\n' \
                              f'⏰<b>Время на оплату:</b> 5 минут\n' \
                              f'➖➖➖➖➖➖➖➖➖➖➖➖\n'


        if await payment_table.get_payment_exists(label) == False:
            await call.message.edit_text(f'<b><i>Заказ не найден, он отменен или не существует.</i></b>')
        else:
            await payment_table.add_payment(label=label,
                                            payment_method='Balance',
                                            invoice_id=label,
                                            )

            await call.message.delete()

            await call.message.answer(text=PRE_PAYMENT_MESSAGE, reply_markup=await pay_balance(category_id=category_id,
                                                                                               server_id=server_id,
                                                                                               quantity=quantity,
                                                                                               label=label,
                                                                                           ))
@dp.callback_query_handler(cb_payment.filter(action='pay_balance'))
async def product_cb(call: types.CallbackQuery, callback_data: dict):
    logger.info(f'Функция product_cb (Balance) {call.message.chat.first_name}')

    pay_method = callback_data.get('action')
    server_id = callback_data.get('server')
    category_id = callback_data.get('category')
    quantity = int(callback_data.get('quantity'))
    label = callback_data.get('label')

    #Из таблицы ID
    user_id_table = await user_table.get_user(call.message.chat.id)

    category_name = await category_table.get_category(category_id=category_id)
    server_name = await server_table.get_server_name(server_id=server_id)
    price_product = await price_table.get_price(server_id=server_id, category_id=category_id)

    payid_time_stamp = await payment_table.get_payment_id(label=label)

    payment_id = payid_time_stamp[0]
    order_time = payid_time_stamp[1]

    balance = await user_table.get_balance(call.message.chat.id)
    await user_table.change_balance(user_id_table,balance-(price_product*quantity))
    await payment_table.change_status_payment(status='paid',label=label)
    reserved_products = await product_table.get_reserved_products(status='reserved',
                                                                  reserved_id=user_id_table,
                                                                  label=label)

    with open(f'{config.ORDERS_PATH}/order_{label}.txt', 'w') as file:
        for reserve_product in reserved_products:
            await basket_table.add_products_to_user(user_id=user_id_table, product_id=reserve_product[0],
                                                    payment_id=payment_id)
            await product_table.change_status(product_id=reserve_product[0], status='sold')
            product = await basket_table.get_product_from_basket(product_id=reserve_product[0])
            file.write(f'{product[1]}:{product[2]}\n')
        file.close()

        await call.message.delete()
        await bot.send_sticker(chat_id=call.message.chat.id,sticker='CAACAgUAAxkBAAELu_Vl93XX3cc3QYnrDskxjBCNnoxjnwACaQgAAjvCkFa-ffrFjBeqqjQE')
        await bot.send_document(chat_id=call.message.chat.id,
                                document=types.InputFile(f'{config.ORDERS_PATH}/order_{label}.txt'),
                                caption=f'➖➖➖➖➖➖➖➖➖➖➖➖\n' \
                                        f'📃 <b>Товар:</b>{category_name} | {server_name}\n' \
                                        f'💰 <b>Цена:</b>{price_product}\n' \
                                        f'📦 <b>Кол-во:</b>{quantity}\n' \
                                        f'💡 <b>Заказ:</b>{label}\n' \
                                        f'🕐 <b>Время заказа:</b>{order_time}\n' \
                                        f'💲 <b>Итоговая сумма:</b>{price_product * quantity}\n' \
                                        f'💲 <b>Способ оплаты:</b>Balance\n' \
                                        f'➖➖➖➖➖➖➖➖➖➖➖➖\n\n'
                                        f'<b>Оставьте отзыв тут:</b>'
                
                                        f'<b><i>Рандомным образом могу выслать баланс тому ,кто оставил отзыв.\n'
                                        f'Спасибо</i></b>\n'
                                )




