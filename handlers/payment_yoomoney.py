import asyncio
import datetime
import logging

from aiogram import types
from db.payment_db import PaymentTable
from keyboards.inline_category import *
from main import dp, bot
from src.utils import create_invoice_yoomoney,invoice_yoomoney_task

user_table = DataBase('database.db')
category_table = CategoryTable('database.db')
product_table = ProductTable('database.db')
server_table = ServerTable('database.db')
basket_table = BasketTable('database.db')
price_table = PriceTable('database.db')
payment_table = PaymentTable('database.db')

logger = logging.getLogger('app.payment_yoomoney')

@dp.callback_query_handler(cb_payment.filter(action='YooMoney'))
async def product_cb(call: types.CallbackQuery, callback_data: dict):
    logger.info(f'Функция product_cb (Yoomoney) {call.message.chat.first_name}')
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
                          f'📃 <b>Товар:</b>{category_name} | {server_name}\n' \
                          f'💰 <b>Цена:</b>{price_product}\n' \
                          f'📦 <b>Кол-во:</b>{quantity}\n' \
                          f'💡 <b>Заказ:</b><i><code>#{label}</code></i>\n' \
                          f'🕐 <b>Время заказа:</b>{order_time}\n' \
                          f'💲 <b>Итоговая сумма:</b>{price_product * quantity} руб.\n' \
                          f'💲 <b>Способ оплаты:</b>{pay_method}\n\n' \
                          f'⏰ <b>Время на оплату:</b> 5 минут\n' \
                          f'➖➖➖➖➖➖➖➖➖➖➖➖\n'

    invoice_result = await create_invoice_yoomoney(price_product * quantity,label=label)

    user_id = await user_table.get_user(call.message.chat.id)

    if await payment_table.get_payment_exists(label) == False:
        # Вынести в конфиг сообщений
        await call.message.edit_text(f'<b><i>Заказ не найден, он отменен или не существует.</i></b>')
    else:
        await payment_table.add_payment(label=label,
                                        payment_method='YooMoney',
                                        invoice_id=invoice_result[1],
                                        )

    await call.message.delete()
    message_id = await call.message.answer(text=PRE_PAYMENT_MESSAGE,
                                           reply_markup=await payment_menu(url=invoice_result[0],
                                                                           category_id=category_id,
                                                                           server_id=server_id,
                                                                           quantity=quantity,
                                                                           label=label,
                                                                           flag='YooMoney'))

    asyncio.create_task(invoice_yoomoney_task(bot=bot,
                                              label=label,
                                              user_id=user_id,
                                              quantity=quantity,
                                              category_id=category_id,
                                              server_id=server_id,
                                              message_id=message_id))

#@dp.callback_query_handler(cb_payment.filter(action='check_payment_yoomoney'))
#async def check_payment_cb(call: types.CallbackQuery, callback_data: dict):
#
#    server_id = callback_data.get('server')
#    category_id = callback_data.get('category')
#    quantity = int(callback_data.get('quantity'))
#    label = callback_data.get('label')
#
#    category_name = await category_table.get_category(category_id=category_id)
#    server_name = await server_table.get_server_name(server_id=server_id)
#    price_product = await price_table.get_price(server_id=server_id, category_id=category_id)
#
#    user_id = await user_table.get_user(call.message.chat.id)
#
#    client = Client(token=config.YOOMONEY_TOKEN)
#    history = client.operation_history(label=label)
#    try:
#        #Срабатывает 'success' если есть operation , то есть заказ если оплачен
#        operation = history.operations[-1]
#        if operation.status == 'success':
#
#            payid_time_stamp = await payment_table.get_payment_id(label=label)
#
#            payment_id = payid_time_stamp[0]
#            order_time = payid_time_stamp[1]
#
#            await payment_table.update_status(status='paid', label=label)
#
#            reserved_products = await product_table.get_reserved_products(status='reserved',
#                                                                          reserved_id=user_id,
#                                                                          label=label)
#            await call.message.delete()
#
#            with open(f'order_{label}.txt', 'w') as file:
#                for reserve_product in reserved_products:
#                    await basket_table.add_products_to_user(user_id=user_id, product_id=reserve_product[0],
#                                                            payment_id=payment_id)
#                    await product_table.change_status(product_id=reserve_product[0], status='sold')
#                    product = await basket_table.get_product_from_basket(product_id=reserve_product[0])
#                    file.write(f'{product[1]}:{product[2]}\n')
#                await bot.send_document(chat_id=call.message.chat.id, document=types.InputFile(f'order_{label}.txt'),
#                                        caption=f'➖➖➖➖➖➖➖➖➖➖➖➖\n' \
#                                                f'📃 Товар:{category_name} | {server_name}\n' \
#                                                f'💰 Цена:{price_product}\n' \
#                                                f'📦 Кол-во:{quantity}\n' \
#                                                f'💡 Заказ:<code>{label}</code>\n' \
#                                                f'🕐 Время заказа:{order_time}\n' \
#                                                f'💲 Итоговая сумма:{price_product * quantity}\n' \
#                                                f'💲 Способ оплаты:YooMoney\n' \
#                                                f'➖➖➖➖➖➖➖➖➖➖➖➖\n'
#                                                f'Оставьте отзыв тут: https://zelenka.guru/'
#
#                                        )
#    except Exception as e:
#        time_payment_status = await payment_table.get_payment_status(label=label)
#        if time_payment_status == 'unpaid':
#            await call.message.delete()
#            await call.message.answer('Заказ не найден,отменен или не существует')
#        else:
#            await call.answer('Вы еще не оплатили свой заказ')
#        pass
#
#
#
##Если заказ удален (истекло время ) и не оплачен



