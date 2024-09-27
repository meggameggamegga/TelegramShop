import asyncio
import datetime
import logging
from aiogram import types

from db.payment_db import PaymentTable
from keyboards.inline_category import *
from main import dp, bot
from src.utils import create_invoice_crystalpay, invoice_crystalpay_task

user_table = DataBase('database.db')
category_table = CategoryTable('database.db')
product_table = ProductTable('database.db')
server_table = ServerTable('database.db')
basket_table = BasketTable('database.db')
price_table = PriceTable('database.db')
payment_table = PaymentTable('database.db')

logger = logging.getLogger('app.payment_crystalpay')

@dp.callback_query_handler(cb_payment.filter(action='CrystalPay'))
async def product_cb(call: types.CallbackQuery, callback_data: dict):
    logger.info(f'Функция product_cb (CrystalPay) {call.message.chat.first_name}')

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
                          f'⏰<b>Время на оплату:</b> 5 минут\n' \
                          f'➖➖➖➖➖➖➖➖➖➖➖➖\n'

    ##Мб вынести в отдельную функцию создание платежа?
    invoice_result = await create_invoice_crystalpay(price_product*quantity)

    user_id = await user_table.get_user(call.message.chat.id)
    if await payment_table.get_payment_exists(label) == False:
        await call.message.edit_text(f'<b><i>Заказ не найден, он отменен или не существует.</i></b>')
    else:
        await payment_table.add_payment(label=label,
                                        payment_method='CrystalPay',
                                        invoice_id=invoice_result[1],
                                        )

        await call.message.delete()

        message_id = await call.message.answer(text=PRE_PAYMENT_MESSAGE, reply_markup=await payment_menu(url=invoice_result[0],
                                                                                                       category_id=category_id,
                                                                                                       server_id=server_id,
                                                                                                       quantity=quantity,
                                                                                                       label=label,
                                                                                                       flag='CrystalPay'))
        #В этой таске проверять если время на оплату прошло и удалять
        asyncio.create_task(invoice_crystalpay_task(id=invoice_result[1],
                                                    bot=bot,
                                                    label=label,
                                                    user_id=user_id,
                                                    quantity=quantity,
                                                    category_id=category_id,
                                                    server_id=server_id,
                                                    message_id=message_id))




