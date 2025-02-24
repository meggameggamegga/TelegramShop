import asyncio
import datetime
import logging

from aiogram import types

from db.payment_db import PaymentTable
from keyboards.inline_category import *
from main import dp, bot
from src.utils import create_invoice_cryptobot, invoice_cryptobot_task

user_table = DataBase('database.db')
category_table = CategoryTable('database.db')
product_table = ProductTable('database.db')
server_table = ServerTable('database.db')
basket_table = BasketTable('database.db')
price_table = PriceTable('database.db')
payment_table = PaymentTable('database.db')

logger = logging.getLogger('app.payment_cryptobot')

@dp.callback_query_handler(cb_payment.filter(action='CryptoBot'))
async def product_cb(call: types.CallbackQuery, callback_data: dict):
    logger.info(f'Функция product_cb (CryptoBot) {call.message.chat.first_name}')
    pay_method = callback_data.get('action')
    server_id = callback_data.get('server')
    category_id = callback_data.get('category')
    quantity = int(callback_data.get('quantity'))
    label = callback_data.get('label')

    category_name = await category_table.get_category(category_id=category_id)
    server_name = await server_table.get_server_name(server_id=server_id)
    price_product = await price_table.get_price(server_id=server_id, category_id=category_id)


    order_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

    PRE_PAYMENT_MESSAGE = f'➖➖➖➖➖➖➖➖➖➖➖➖\n' \
                          f'📃<b>Товар:</b> {category_name} | {server_name}\n' \
                          f'💰<b>Цена:</b> {price_product}\n' \
                          f'📦<b>Кол-во:</b> {quantity}\n' \
                          f'💡<b>Заказ:</b> <i><code>#{label}</code></i>\n' \
                          f'🕐<b>Время заказа:</b> {order_time}\n' \
                          f'💲<b>Итоговая сумма:</b> {price_product * quantity} руб.\n' \
                          f'💲<b>Способ оплаты:</b> {pay_method}\n\n' \
                          f'⏰<b>Время на оплату:</b>  5 минут\n' \
                          f'➖➖➖➖➖➖➖➖➖➖➖➖\n'

    #Мб вынести в отдельную функцию создание платежа?

    invoice_result = await create_invoice_cryptobot(price_product,quantity)

    user_id = await user_table.get_user(call.message.chat.id)

    if await payment_table.get_payment_exists(label) == False:
        #Вынести в конфиг сообщений
        await call.message.edit_text(f'<b><i>Заказ не найден, он отменен или не существует.</i></b>')
    else:
        await payment_table.add_payment(label=label,
                                        payment_method='CryptoBot',
                                        invoice_id=invoice_result[1],
                                        )
        await call.message.delete()
        message_id = await call.message.answer(text=PRE_PAYMENT_MESSAGE,
                                               reply_markup=await payment_menu(url=invoice_result[0],
                                                                               category_id=category_id,
                                                                               server_id=server_id,
                                                                               quantity=quantity,
                                                                               label=label,
                                                                               flag='CryptoBot'))


        asyncio.create_task(invoice_cryptobot_task(id=invoice_result[1],
                                                    bot=bot,
                                                    label=label,
                                                    user_id=user_id,
                                                    quantity=quantity,
                                                    category_id=category_id,
                                                    server_id=server_id,
                                                    message_id=message_id))

#@dp.callback_query_handler(cb_payment.filter(action='check_payment_cryptobot'))
#async def check_payment_cb(call: types.CallbackQuery, callback_data: dict):
#
#    server_id = callback_data.get('server')
#    category_id = callback_data.get('category')
#    quantity = int(callback_data.get('quantity'))
#    label = callback_data.get('label')
#
#    category_name = await category_table.get_category(category_id=category_id)
#    server_name = await server_table.get_server_name(server_id=server_id)
#    price_product = await price_table.get_price(server_id=server_id,category_id=category_id)
#
#    user_id = await user_table.get_user(call.message.chat.id)
#
#    crypto = AioCryptoPay(token=config.CRYPTOBOT_TOKEN, network=Networks.TEST_NET)
#    invoice_id = await payment_table.get_invoice_id(label=label)
#
#    invoice_payment = await crypto.get_invoices(invoice_ids=invoice_id)
#
#    if invoice_payment[0].status == 'active':
#        #Тут проверить статус заказа из бд (если не оплатил и
#        time_payment_status = await payment_table.get_payment_status(label=label)
#        if time_payment_status == 'unpaid':
#            await call.message.delete()
#            await call.message.answer('Заказ не найден,отменен или не существует')
#        else:
#            await call.answer('Вы еще не оплатили свой заказ')
#
#    if invoice_payment[0].status == 'paid':
#
#        payid_time_stamp = await payment_table.get_payment_id(label=label)
#
#        payment_id = payid_time_stamp[0]
#        order_time = payid_time_stamp[1]
#        await payment_table.update_status(status='paid', label=label)
#
#         # Достали зарезервированые продукты
#        reserved_products = await product_table.get_reserved_products(status='reserved',
#                                                                      reserved_id=user_id,
#                                                                      label=label)
#
#        await call.message.delete()
#        with open(f'order_{label}.txt','w') as file:
#            for reserve_product in reserved_products:
#                await basket_table.add_products_to_user(user_id=user_id, product_id=reserve_product[0], payment_id=payment_id)
#                await product_table.change_status(product_id=reserve_product[0],status='sold')
#                product = await basket_table.get_product_from_basket(product_id=reserve_product[0])
#                file.write(f'{product[1]}:{product[2]}\n')
#        try:
#            await bot.send_document(chat_id=call.message.chat.id,document=types.InputFile(f'order_{label}.txt'),
#                                    caption=f'➖➖➖➖➖➖➖➖➖➖➖➖\n' \
#                                            f'📃 Товар:{category_name} | {server_name}\n' \
#                                            f'💰 Цена:{price_product}\n' \
#                                            f'📦 Кол-во:{quantity}\n' \
#                                            f'💡 Заказ:{label}\n' \
#                                            f'🕐 Время заказа:{order_time}\n' \
#                                            f'💲 Итоговая сумма:{price_product * quantity}\n' \
#                                            f'💲 Способ оплаты:CryptoBOT\n' \
#                                            f'➖➖➖➖➖➖➖➖➖➖➖➖\n'
#                                            f'Оставьте отзыв тут: https://zelenka.guru/'
#                                    )
#        except Exception as e:
#            await call.message.answer('Заказ не найден, он отменен или не существует')
#            pass
#
#
#    await crypto.close()
#