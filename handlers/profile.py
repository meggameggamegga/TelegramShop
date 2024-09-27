import logging
from datetime import datetime, timedelta

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import ContentType


import config
from db.payment_db import PaymentTable
from keyboards.profile_inline import *
from main import bot,dp
from db.database import DataBase
from src.checker import Auth
from states.state_user import getLabel

user_table = DataBase('database.db')
category_table = CategoryTable('database.db')
product_table = ProductTable('database.db')
server_table = ServerTable('database.db')
basket_table = BasketTable('database.db')
payment_table = PaymentTable('database.db')

logger = logging.getLogger('app.profile')

@dp.message_handler(text=config.PROFILE_BTN, content_types=ContentType.TEXT)
async def profile_cmnd(message: types.Message):
    logger.info(f'Функция profile_cmnd {message.from_user.first_name}')
    user_id_table = await user_table.get_user(message.from_user.id)
    user_balance = await user_table.get_balance(message.from_user.id)
    await message.answer(f'<b>👤 Пользователь:</b> {message.from_user.username}\n'
                         f'<b>🆔 ID:</b> {user_id_table}\n'
                         f'<b>💰 Баланс:</b> {user_balance}',
                         reply_markup=await profile_menu(user_id_table))






#@dp.callback_query_handler(cb_profile_pagination.filter(action='pagination'))
#@dp.callback_query_handler(cb_profile.filter(action='payment_history'))
#async def profile_payment_cmnd(call: types.CallbackQuery, callback_data: dict):
#    user_id_table = callback_data.get('user_id')
#    ITEMS_PER_PAGE = 5
#    payments = await payment_table.get_payments(status='paid', user_id=user_id_table)
#    total_payments = len(payments)
#
#    if total_payments > 0:
#        page = int(callback_data.get('page', 1))
#        start_index = (page - 1) * ITEMS_PER_PAGE
#        end_index = start_index + ITEMS_PER_PAGE
#        current_payments = payments[start_index:end_index]
#
#        text = ''
#        for payment in current_payments:
#            label = payment[1]
#            payment_method = payment[3]
#            amount = payment[4]
#            payment_data = payment[7]
#            text += f'<b>Заказ:</b><i><code>#{label}</code></i>\n' \
#                    f'<b>Время оплаты:</b> {payment_data}\n' \
#                    f'<b>Итоговая сумма:</b> {amount} руб. \n' \
#                    f'<b>Способ оплаты:</b> {payment_method}\n\n'
#
#
#        await call.message.edit_text(text, reply_markup=await pagination_menu(start_index,
#                                                                              user_id_table,
#                                                                              end_index,
#                                                                              total_payments,
#                                                                              page))
#    else:
#        await call.message.edit_text('<b>У вас нет платежей </b>', reply_markup=await profile_back())
#
@dp.callback_query_handler(cb_profile_pagination.filter(action='pagination_payments'))
@dp.callback_query_handler(cb_profile.filter(action='payment_history'))
async def profile_payment_cmnd(call: types.CallbackQuery,callback_data:dict):
    logger.info(f'Функция profile_payment_cmnd {call.message.chat.first_name}')
    text = '➖➖➖➖➖➖➖➖➖➖➖➖\n\n'
    count_payments = 5
    user_id_table = await user_table.get_user(call.message.chat.id)

    labels = []

    payments = await payment_table.get_payments(status='paid', user_id=user_id_table)
    total_payment = len(payments)

    if total_payment > 0:

        page = int(callback_data.get('page',1))
        start_index = (page-1) * count_payments
        end_index = start_index + count_payments
        payments = payments[start_index:end_index]

        for payment in payments:
            label = payment[1]
            labels.append(label)
            payment_method = payment[3]
            amount = payment[4]
            payment_data = payment[7]
            count_payments +=1
            text += f'<b>🛒 Заказ:</b> <i><code>#{label}</code></i>\n' \
                    f'<b>⏰ Время оплаты:</b> {payment_data}\n' \
                    f'<b>💰 Итоговая сумма:</b> {amount} руб. \n' \
                    f'<b>💳 Способ оплаты:</b> {payment_method}\n\n'
        text+='\n➖➖➖➖➖➖➖➖➖➖➖➖'
        await call.message.edit_text(text,reply_markup=await pagination_menu_payments(page=page,
                                                                             user_id_table=user_id_table,
                                                                             end_index=end_index,
                                                                             total_payments=total_payment,
                                                                             start_index=start_index,
                                                                             labels=labels))

    else:
        await call.message.delete()
        await call.message.answer('<b>У вас нет покупок или платежей</b>',reply_markup=await profile_back())



@dp.callback_query_handler(cb_profile_back.filter(action='back'))
async def back_profile_cmnd(call: types.CallbackQuery):
    logger.info(f'Функция back_profile_cmnd {call.message.chat.first_name}')
    user_id_table = await user_table.get_user(call.message.chat.id)
    user_balance = await user_table.get_balance(call.message.chat.id)
    await call.message.delete()
    await call.message.answer(f'<b>👤 Пользователь:</b> {call.message.chat.username}\n'
                              f'<b>🆔 ID:</b> {user_id_table}\n'
                              f'<b>💰 Баланс:</b> {user_balance}',
                              reply_markup=await profile_menu(user_id_table))


#-----------История заказов--------------#


@dp.callback_query_handler(cb_profile_send_order.filter(action='send_order'))
async def send_order_cmnd(call: types.CallbackQuery,callback_data:dict):
    logger.info(f'Функция send_order_cmnd {call.message.chat.first_name}')
    label = callback_data.get('label')
    user_id_table = await user_table.get_user(call.message.chat.id)

    user_products = await product_table.get_user_products(label)
    server_name = await server_table.get_server_name(user_products[1])
    category_name = await category_table.get_category(user_products[0])
    payment_info = await payment_table.get_payments_full(user_id=user_id_table,label=label)


    await call.message.edit_text(f'➖➖➖➖➖➖➖➖➖➖➖➖\n\n'
                                 f'🛒 <b>Заказ:</b> <i><code>#{label}</code></i>\n'
                                 f'📦 <b>Имя товара:</b> {server_name} - {category_name}\n'
                                 f'⏰ <b>Дата платежа:</b> {payment_info[7]}\n'
                                 f'💸 <b>Итоговая сумма:</b> {payment_info[4]} руб.\n'
                                 f'💳 <b>Способ оплаты:</b> {payment_info[3]}\n'
                                 f'\n➖➖➖➖➖➖➖➖➖➖➖➖',
                                 reply_markup=await send_order_profile(label=label))



@dp.callback_query_handler(cb_profile_send_order.filter(action='send_order_file'))
async def send_order_file(call:types.CallbackQuery,callback_data:dict):
    logger.info(f'Функция send_order_file {call.message.chat.first_name}')
    label = callback_data.get('label')

    user_id_table = await user_table.get_user(call.message.chat.id)
    user_balance = await user_table.get_balance(call.message.chat.id)

    await call.message.delete()
    await bot.send_document(call.message.chat.id, document=types.InputFile(f'{config.ORDERS_PATH}/order_{label}.txt'))
    await bot.send_message(chat_id=call.message.chat.id,
                           text=f'<b>👤 Пользователь:</b> {call.message.chat.username}\n'
                                f'<b>🆔 ID:</b> {user_id_table}\n'
                                f'<b>💰 Баланс:</b> {user_balance}',
                           reply_markup=await profile_menu(user_id_table))

#@dp.callback_query_handler(cb_profile_pagination.filter(action='pagination_orders'))
#@dp.callback_query_handler(cb_profile.filter(action='orders_history'))
#async def profile_orders_cmnd(call: types.CallbackQuery,callback_data:dict):
#
#    text = ''
#
#    count_orders = 5
#
#    user_id_table = callback_data.get('user_id')
#
#    products = await basket_table.basket_product_group(user_id_table)
#    print(products)
#    count_products = len(products)
#    if count_products > 0:
#        page = int(callback_data.get('page',1))
#        start_index = (page-1) * count_orders
#        end_index = start_index+count_orders
#        products = products[start_index:end_index]
#        for product in products:
#            payment_id = product[0]
#            products_ids = product[1]
#            users_id = product[0]
#            label = product[3]
#            #Мб тут по лейблу брать определенный платеж и дозаполнить данными
#            payment_info = await payment_table.get_payment_from_label(label)
#            payment_method = payment_info[3]
#            payment_time_stamp = payment_method[7]
#
#            text += f'Заказ:#{label}\n' \
#                    f'Время заказа: {payment_time_stamp}\n' \
#                    f'Итоговая сумма: {payment_info[3]}\n' \
#                    f'Способ оплаты:{payment_info[2]}\n\n'
#    #    await call.message.edit_text(text,reply_markup=await pagination_menu_orders(start_index=start_index,
#                                                                             #end_index=end_index,
#                                                                             #user_id_table=user_id_table,
#                                                                             #total_payments=count_products,
#                                                                             #page=page))
#    #else:
#    #    await call.message.delete()
#   ##     await call.message.answer('У вас нет покупок')

@dp.callback_query_handler(cb_profile_get_change.filter(action='get_replace'))
async def get_change_menu(call:types.CallbackQuery,state:FSMContext):
    await call.answer()
    await call.message.delete()
    await call.message.answer(f'Введите ID покупки')
    await getLabel.label.set()


@dp.message_handler(state=getLabel.label.state)
async def check_label(message:types.Message,state:FSMContext):
    print(f'Функция для {message.from_user.first_name}')
    label = message.text
    if not label.isdigit() and len(label) != 7:
        await message.answer('Не правильный формат\n'
                             'Скопируйте ID покупки и пришлите снова.\n')
        await state.reset_state()
    else:
        user_id_table = await user_table.get_user(message.from_user.id)

        payment = await payment_table.get_payment_from_user_label(user_id=user_id_table,label=label)
        if payment is None:
            await message.answer('Платеж не найден')
        else:
            status = payment[1]
            time_stamp = payment[2]
            products = await product_table.get_log_pas_label(label)
            user_balance = await user_table.get_balance(message.from_user.id)
            print(user_balance,'Балнс пользователя')
            price = await price_table.get_price(server_id=products[0][3],category_id=products[0][2])
            print(price,'Цена товара')
            if len(products)>1:
                await message.answer('Автозамена находится в тестовом режим.\n'
                                     'Получить замену можно,если куплен только один аккаунт\n')
                await state.reset_state()
            else:
                check_status = await product_table.get_checked(label)
                if check_status is not None:
                    await message.answer('Аккаунт уже проверялся!')
                    await state.reset_state()
                else:
                    delta_time = datetime.strptime(time_stamp, '%Y-%m-%d %H:%M') + timedelta(minutes=15)
                    if status == 'paid' and delta_time.now() <= delta_time:
                        login = products[0][0]
                        password = products[0][1]
                        client = Auth()
                        #тут проверять на невалид , если еще идет слишком много запросов
                        #try:
                        acc_token = await client.temp_auth(username=login.strip(), password=password.strip())
                        #print(acc_token,'Аунтификация ')
                        if acc_token is None:
                            print(f'Баланс юзеру {message.from_user.first_name}')
                            # Тут сделать колонку ,аккаунт проверялся или нет.
                            await product_table.set_checked(1, label)
                            await user_table.change_balance(user_id_table, user_balance+price)
                            print('Баланс изменил на',user_balance+price)
                            await message.answer(f'💰 <b>Вам начислен баланс {price}</b>')
                        else:
                            banned = await client.check_ban(acc_token)
                            if banned:
                                print(f'Баланс юзеру {message.from_user.first_name}')
                                #Тут сделать колонку ,аккаунт проверялся или нет.
                                await product_table.set_checked(1,label)
                                await user_table.change_balance(user_id_table, user_balance+price)
                                print('Баланс изменил на', user_balance + price)
                                await message.answer(f'💰 <b>Вам начислен баланс {price}</b>')
                                #await state.reset_state()
                            else:
                                await message.answer('<b>Аккаунт валидный</b>')
                                await product_table.set_checked(1, label)
                            #except Exception as e:
                            #    print('При чеке аккаунта произошла ошибка')
                            #    await message.answer('Произошла ошибка,напишите по контактам в "Поддержка"')
                                #await state.reset_state()
                    else:
                        await message.answer('Аккаунт не оплачен или закончилась гарантия')
        await state.reset_state()



