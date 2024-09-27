import logging
from datetime import datetime, timedelta
import random
import string
import asyncio

from LOLZTEAM import Market, Constants
from aiocryptopay import AioCryptoPay, Networks
from aiogram import types, Bot
from aiogram.types import Message
from crystalpayio import CrystalPayIO
from yoomoney import Quickpay, Client

import config
from db.basket_db import BasketTable
from db.category_db import CategoryTable
from db.database import DataBase
from db.payment_db import PaymentTable
#тут изменить ссылки
from db.price_db import PriceTable
from db.product_db import ProductTable
from db.server_db import ServerTable

db_path = './database.db'

user_table = DataBase(db_path)
category_table = CategoryTable(db_path)
product_table = ProductTable(db_path)
server_table = ServerTable(db_path)
basket_table = BasketTable(db_path)
price_table = PriceTable(db_path)
payment_table = PaymentTable(db_path)

crystal = CrystalPayIO(config.CRYSTALPAY_LOGIN, config.CRYSTALPAY_SECRET)
crypto = AioCryptoPay(token=config.CRYPTOBOT_TOKEN, network=Networks.MAIN_NET)
client = Client(token=config.YOOMONEY_TOKEN)

logger = logging.getLogger('app.utils')



async def generate_label() -> str:
    a = str(string.digits)
    random.shuffle(list(a))
    label = ''.join([random.choice(a) for _ in range(7)])
    return label



async def send_pre_order_message(bot:Bot,user_id:int,label):
    logger.info('Функция send_pre_order_message')
    #Тут получаю user_id через ID из таблицы
    user_chat_id = await user_table.get_user_id(user_id)

    #await bot.delete_message(chat_id=user_chat_id,message_id=message_id.message_id)
    await bot.send_message(chat_id=user_chat_id,
                           text=f'<b>Заказ <i><code>#{label}</code></i> отменен</b>',
                            )

    await payment_table.delete_payment(label=label)
    await product_table.unreserved_product(status='available',label=label)

async def send_order_message(bot:Bot,user_id:int,label,message_id):
    logger.info('Функция send_order_message')
    #Тут получаю user_id через ID из таблицы
    user_chat_id = await user_table.get_user_id(user_id)

    await bot.delete_message(chat_id=user_chat_id,message_id=message_id.message_id)
    await bot.send_message(chat_id=user_chat_id,
                           text=f'<b>Заказ <i><code>#{label}</code></i> отменен</b>',
                            )

    await payment_table.change_status_payment(label=label,status='unpaid')
    await product_table.unreserved_product(status='available',label=label)

async def task_check_payment(bot: Bot):
    while True:
        payid_timestamp = await payment_table.get_uncreation_payments()
        for payment in payid_timestamp:
            label = payment[0]
            user_id_table = payment[1]
            time_stamp = payment[2]
            original_time = datetime.strptime(time_stamp, '%Y-%m-%d %H:%M') + timedelta(minutes=5.30)
            if datetime.now() >= original_time:
                user_id = await user_table.get_user_id(user_id_table)
                await payment_table.delete_payment(label=label)
                await product_table.unreserved_product(status='available', label=label)

                await bot.send_message(chat_id=user_id,
                                       text=f'<b>Заказ <i><code>#{label}</code></i> отменен</b>',
                                       )
        await asyncio.sleep(120)

#async def task_check_payment_test(bot:Bot, label, user_id):
#    while True:  #Искать если только не выбран платежний метод иначе отмени
#        logger.info('Функция task_check_payment')
#        try:
#            #Получать список платежей из бд которые active
#            #Брать user_id через user_id_table
#            #Если время платежа истекло, делать аккаунт активным
#            #Удалять платеж
#            #Отсылать сообщению пользователю
#            payment_method = await payment_table.get_payment_method_exist(label=label)
#            payid_timestamp = await payment_table.get_payment_id(label=label)
#            original_time = datetime.strptime(payid_timestamp[1], '%Y-%m-%d %H:%M') + timedelta(minutes=2)#Обратно вернуть время 5.30
#            if datetime.now() >= original_time and payment_method is None:
#                await send_pre_order_message(bot, user_id, label)
#        except Exception as e:
#            break
#            pass
#        await asyncio.sleep(120)




async def create_invoice_crystalpay(price:int) -> tuple:
    logger.info('Функция create_invoice_crystalpay')
    invoice = await crystal.invoice.create(
        amount=price, # Цена
        lifetime=5, # Время жизни чека (в минутах)
        amount_currency="RUB",
        redirect_url=''
    )
    return (invoice.url, invoice.id)


async def create_invoice_cryptobot(price_product,quantity):
    logger.info('Функция create_invoice_cryptobot')
    rates = await crypto.get_exchange_rates()
    rate_usdt = [rate.rate for rate in rates if rate.source == 'USDT' and rate.target == 'RUB'][0]
    cur_price = (price_product * quantity) / rate_usdt
    invoice = await crypto.create_invoice(asset='USDT', amount=round(cur_price, 5))
    url_prefix = invoice.hash
    invoice_id = invoice.invoice_id
    await crypto.close()
    return (url_prefix,invoice_id)


async def create_invoice_yoomoney(price_product,label) -> tuple:
    logger.info('Функция create_invoice_yoomoney')
    quickpay = Quickpay(
        receiver=config.YOOMONEY_CARD,
        quickpay_form="shop",
        targets="TG_SHOP",
        paymentType="SB",
        sum=price_product,
        label=f'{label}',
        successURL='',
    )
    return (quickpay.redirected_url,quickpay.label)


async def create_invoice_lolz(label,amount):
    market = Market(token=config.LOLZ_TOKEN, language="ru")
    payment_url = market.payments.generate_link(user_id=config.LOLZ_USERID,
                                                amount=amount,
                                                comment=label,
                                                redirect_url='',
                                                currency=Constants.Market.Currency.rub)
    return payment_url

async def invoice_crystalpay_task(bot:Bot,id: str,label:str,user_id,quantity,category_id,server_id,message_id) -> None:
    while True:
        logger.info('Функция invoice_crystalpay_task')
        invoice = await crystal.invoice.get(id)
        payid_timestamp = await payment_table.get_payment_id(label=label)
        original_time = datetime.strptime(payid_timestamp[1], '%Y-%m-%d %H:%M') + timedelta(minutes=5)
        payment_status = await payment_table.get_payment_status(label=label)
        #Сделать логику если он выбрал платежку , но не стал дальше оплачивать
        if invoice.state == "payed" and payment_status == 'active':
            user_chat_id = await user_table.get_user_id(user_id)
            #Изменили статус платежа на оплачено
            await payment_table.change_status_payment(status='paid',label=label)
            await bot.edit_message_text(chat_id=user_chat_id,text=f"✅<b>Заказ <i><code>#{label}</code></i> оплачен</b>",
                                        message_id=message_id.message_id)
            #Тут вызвать функция которая вышлет аккаунт
            await send_account_to_user(label=label,
                                       user_id=user_id,
                                       quantity=quantity,
                                       category_id=category_id,
                                       server_id=server_id,
                                       bot=bot,
                                       payment_name='CrystalPay')
            break
        elif payment_status == 'active' and datetime.now() >= original_time:
            await payment_table.change_status_payment(label=label,status='unpaid')
            await product_table.unreserved_product(status='available', label=label)
            await send_order_message(bot=bot,
                                     user_id=user_id,
                                     label=label,
                                     message_id=message_id)
            break


        await asyncio.sleep(20)  # Задержка

async def invoice_cryptobot_task(bot:Bot,id: int,label:str,user_id,quantity,category_id,server_id,message_id) -> None:
    while True:
        print(f'В цикле для {user_id}')
        logger.info('Функция invoice_cryptobot_task')
        invoice = await crypto.get_invoices(invoice_ids=id)
        payment_status = await payment_table.get_payment_status(label=label)
        payid_timestamp = await payment_table.get_payment_id(label=label)
        original_time = datetime.strptime(payid_timestamp[1], '%Y-%m-%d %H:%M') + timedelta(minutes=5)

        if invoice.status == "paid" and payment_status == 'active':
            user_chat_id = await user_table.get_user_id(user_id)
            #Изменили статус платежа на оплачено
            await payment_table.change_status_payment(status='paid',label=label)
            await bot.edit_message_text(chat_id=user_chat_id,text=f"✅<b>Заказ <i><code>#{label}</code></i> успешно оплачен</b>",
                                        message_id=message_id.message_id)
            #Тут вызвать функция которая вышлет аккаунт
            await send_account_to_user(label=label,
                                       user_id=user_id,
                                       quantity=quantity,
                                       category_id=category_id,
                                       server_id=server_id,
                                       bot=bot,
                                       payment_name='CryptoBot')

            break
        elif payment_status == 'active' and datetime.now() >= original_time:
            await payment_table.change_status_payment(label=label, status='unpaid')
            await product_table.unreserved_product(status='available', label=label)
            await send_order_message(bot=bot,
                                     user_id=user_id,
                                     label=label,
                                     message_id=message_id)
            break
        elif payment_status == 'canceled':
            await crypto.delete_invoice(invoice_id=id)
            print('Удалил платеж из CryptoBot')
            break
        await crypto.close()
        await asyncio.sleep(20)


#Проверять типо, если "Отмена" , то не отправлять сообщение и отменить таску

async def invoice_yoomoney_task(label,bot:Bot,user_id,message_id,quantity,category_id,server_id):
    while True:
        logger.info('Функция invoice_yoomoney_task')
        payment_status = await payment_table.get_payment_status(label=label)
        payid_timestamp = await payment_table.get_payment_id(label=label)
        original_time = datetime.strptime(payid_timestamp[1], '%Y-%m-%d %H:%M') + timedelta(minutes=5)
        history = client.operation_history(label=label)

        try:
            operation = history.operations[-1]
            if operation.status == 'success' and payment_status == 'active':
                user_chat_id = await user_table.get_user_id(user_id)
                await payment_table.update_status(status='paid', label=label)
                await bot.edit_message_text(chat_id=user_chat_id,
                                            text=f"✅Заказ <i><code>#{label}</code></i> оплачен!",
                                            message_id=message_id.message_id)
                await send_account_to_user(label=label,
                                           user_id=user_id,
                                           quantity=quantity,
                                           category_id=category_id,
                                           server_id=server_id,
                                           bot=bot,
                                           payment_name='YooMoney')
                break
        except Exception as e:
            if payment_status == 'canceled':
                print('Платеж отменен')
                break
            if payment_status == 'active' and datetime.now() >= original_time:
                await payment_table.change_status_payment(label=label, status='unpaid')
                await product_table.unreserved_product(status='available', label=label)
                await send_order_message(bot=bot,
                                         user_id=user_id,
                                         label=label,
                                         message_id=message_id)
                break
        await asyncio.sleep(20)

async def invoice_lolz_task(label,bot:Bot,user_id,message_id,quantity,category_id,server_id):
    while True:
        logger.info('Функция invoice_yoomoney_task')
        payment_status = await payment_table.get_payment_status(label=label)
        payid_timestamp = await payment_table.get_payment_id(label=label)
        original_time = datetime.strptime(payid_timestamp[1], '%Y-%m-%d %H:%M') + timedelta(minutes=5)

        lolz = Market(token=config.LOLZ_TOKEN,language='ru')
        lolz_history = lolz.payments.history(user_id=config.LOLZ_USERID)
        label_exist = lolz_history['payments']['data']

async def send_account_to_user(user_id,label,bot:Bot,category_id,quantity,server_id,payment_name):
    logger.info('Функция send_account_to_user')
    category_name = await category_table.get_category(category_id=category_id)
    server_name = await server_table.get_server_name(server_id=server_id)
    price_product = await price_table.get_price(server_id=server_id, category_id=category_id)

    payid_time_stamp = await payment_table.get_payment_id(label=label)

    payment_id = payid_time_stamp[0]
    order_time = payid_time_stamp[1]
    reserved_products = await product_table.get_reserved_products(status='reserved',
                                                                  reserved_id=user_id,
                                                                  label=label)
    user_chat_id = await user_table.get_user_id(user_id)

    with open(f'{config.ORDERS_PATH}/order_{label}.txt', 'w') as file:
        for reserve_product in reserved_products:
            await basket_table.add_products_to_user(user_id=user_id, product_id=reserve_product[0],
                                                    payment_id=payment_id)
            await product_table.change_status(product_id=reserve_product[0], status='sold')
            product = await basket_table.get_product_from_basket(product_id=reserve_product[0])
            file.write(f'{product[1]}:{product[2]}\n')
        file.close()
        await bot.send_sticker(chat_id=user_chat_id,sticker='CAACAgUAAxkBAAELu_Vl93XX3cc3QYnrDskxjBCNnoxjnwACaQgAAjvCkFa-ffrFjBeqqjQE')
        await bot.send_document(chat_id=user_chat_id,
                                document=types.InputFile(f'{config.ORDERS_PATH}/order_{label}.txt'),
                                caption=f'➖➖➖➖➖➖➖➖➖➖➖➖\n\n' \
                                        f'📃 <b>Товар:</b>{category_name} | {server_name}\n' \
                                        f'💰 <b>Цена:</b>{price_product}\n' \
                                        f'📦 <b>Кол-во:</b>{quantity}\n' \
                                        f'💡 <b>Заказ:</b>{label}\n' \
                                        f'🕐 <b>Время заказа:</b>{order_time}\n' \
                                        f'💲 <b>Итоговая сумма:</b>{price_product * quantity}\n' \
                                        f'💲 <b>Способ оплаты:</b>{payment_name}\n' \
                                        f'\n\n➖➖➖➖➖➖➖➖➖➖➖➖\n\n'
                                        f'<b>Оставьте отзыв тут:</b>'
                                        
                                        f'<b><i>Рандомным образом могу выслать баланс тому ,кто оставил отзыв.\n'
                                        f'Спасибо</i></b>\n'
                                )



