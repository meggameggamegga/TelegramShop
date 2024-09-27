import asyncio
import datetime
import logging

from aiogram import types
import random

from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command

import config
from db.payment_db import PaymentTable
from db.database import DataBase
from filters.admin_filter import IsAdmin
from keyboards.admin_panel import admin_menu, cb_admin, admin_cancel, payment_keyboard, cb_admin_payment, back_keyboard, \
    send_message_kb, cb_admin_send_message
from keyboards.inline_category import *
from keyboards.menu_start import menu_kb
from main import bot,dp
from states.state_admin import AddAccounts, AddCategory, AddBalance, SendMessage

user_table = DataBase('database.db')
category_table = CategoryTable('database.db')
product_table = ProductTable('database.db')
server_table = ServerTable('database.db')
basket_table = BasketTable('database.db')
price_table = PriceTable('database.db')
payment_table = PaymentTable('database.db')

logger = logging.getLogger('app.admin_panel')




@dp.message_handler(IsAdmin(),Command('admin'),state='*')
async def admin_panel(message:types.Message,state:FSMContext):
    user_state = await state.get_state()
    if user_state:
        await state.reset_state()
    logger.info('Функция admin_panel')

    await message.answer('Админ-Панель',reply_markup=await admin_menu())

@dp.callback_query_handler(cb_admin.filter(action='back'),IsAdmin(),state='*')
async def admin_panel(call:types.CallbackQuery,state:FSMContext):
    user_state = await state.get_state()
    if user_state:
        await state.reset_state()
    logger.info('Функция admin_panel')

    await call.message.edit_text('Админ-Панель',reply_markup=await admin_menu())

#-----------------------Добавление аккаунтов--------------------------#

@dp.callback_query_handler(cb_admin.filter(action='add_accounts'))
async def add_accounts_cmnd(call:types.CallbackQuery):
    logger.info('Функция add_accounts_cmnd')
    text = ''
    await call.answer()
    #Тут крч показать какие ID категориев
    categories = await category_table.get_all_categories()
    for category in categories:
        text += f'ID {category[0]} | {category[1]}\n'
    await call.message.answer('Отправьте ID категории\n\n'
                              f'{text}',reply_markup= await admin_cancel())
    await AddAccounts.choose_category.set()

@dp.message_handler(state=AddAccounts.choose_category.state)
async def choose_category(message:types.Message,state:FSMContext):
    logger.info('Функция choose_category')
    text = ''
    async with state.proxy() as data:
        data['category_id'] = message.text
    servers = await server_table.get_all_servers()
    for server in servers:
        text += f'ID {server[0]} | {server[1]}\n'
    await message.answer(f'Сервер ID\n\n'
                         f'{text}',reply_markup=await admin_cancel())
    await AddAccounts.choose_server.set()

@dp.message_handler(state=AddAccounts.choose_server.state)
async def choose_server(message:types.Message,state:FSMContext):
    logger.info('Функция choose_server')
    async with state.proxy() as data:
        data['server_id'] = message.text

    await message.answer('Отправьте файл',reply_markup=await admin_cancel())
    await AddAccounts.send_file.set()

@dp.message_handler(state=AddAccounts.send_file.state,content_types=types.ContentType.DOCUMENT)
async def take_file(message:types.Message,state:FSMContext):
    logger.info('Функция take_file')
    not_added_accs = ''
    async with state.proxy() as data:
        server_id = data['server_id']
        category_id = data['category_id']
    if message.document.mime_type == 'text/plain':
        # Получаем файл

        await message.document.download(r'./accounts/accounts.txt')
        # Получаем содержимое файла
        with open(r'./accounts/accounts.txt', 'r', encoding='utf-8') as file:
            data = file.readlines()
        for account in data:
            login = account.split(':')[0]
            password = account.split(':')[1]
            try:
                await product_table.add_product(login=login,
                                                password=password,
                                                category_id=category_id,
                                                server_id=server_id)
            except Exception as e:
                not_added_accs+=f'{login}\n'
                pass
    await message.answer('Аккаунты добавлены\n'
                         f'Не добавлены\n'
                         f'{not_added_accs}')
    await state.reset_state()


@dp.callback_query_handler(cb_admin.filter(action='cancel_admin'),state='*')
async def cancel_admin_btn(call:types.CallbackQuery,state:FSMContext):
    logger.info('Функция cancel_admin_btn')
    await state.reset_state()
    await call.message.delete()
    await call.message.answer(config.START_MESSAGE, reply_markup=menu_kb())



#--------Добавить баланс юзеру----------------#
@dp.callback_query_handler(cb_admin.filter(action='change_balance'))
async def change_balance(call:types.CallbackQuery):
    await call.message.delete()
    await call.message.answer('Пришлите ID пользователя')

    await AddBalance.send_user_id.set()

@dp.message_handler(state=AddBalance.send_user_id.state)
async def send_balance_user(message:types.Message,state:FSMContext):
    async with state.proxy() as data:
        data['user_id_table'] = int(message.text)

    await message.answer('Какой установить баланс')
    await AddBalance.send_balance.set()

@dp.message_handler(state=AddBalance.send_balance.state)
async def save_balance_user(message:types.Message,state:FSMContext):
    async with state.proxy() as data:
        user_id_table = data['user_id_table']

    balance = int(message.text)

    user_id = await user_table.get_user_id(user_id_table)
    try:
        await user_table.change_balance(user_id_table,balance)

    except Exception as e:
        await message.answer(f'Произошла ошибка в добавление аккауниа {e}')

    await bot.send_message(int(user_id),f'💰 <b>Вам начислен баланс {balance}</b>')
    await message.answer('Баланс изменен,пользователю придет сообщение')

    await state.reset_state()




#--------Кол-во пользователей-------#

@dp.callback_query_handler(cb_admin.filter(action='send_users'))
async def send_users(call:types.CallbackQuery,state:FSMContext):
    await call.answer()
    users = await user_table.get_users()
    MAX_USERS_PER_MESSAGE = 20
    # Разбиваем список пользователей на части по MAX_USERS_PER_MESSAGE
    user_chunks = [users[i:i + MAX_USERS_PER_MESSAGE] for i in range(0, len(users), MAX_USERS_PER_MESSAGE)]
    #Делает из общего списка группы с подсписком по кол-ву отображения
    for chunk in user_chunks:
        answer_text = 'Пользователи\n\n'
        for user in chunk:
            answer_text += f'{str(user[0])} - {str(user[1])} - {str(user[2])}\n'

        # Создаем инлайн-клавиатуру для перелистывания пользовате

        await call.message.answer(answer_text)

@dp.callback_query_handler(cb_admin.filter(action='category_price'))
async def get_category_price(call:types.CallbackQuery):
    text = ''
    await call.answer()
    data = await price_table.get_category_server_price()
    for info in data:
        price = info[1]
        category_id = info[2]
        category_name = info[3]
        server_id = info[4]
        server_name = info[5]
        if f'<b>Имя категории:</b>{category_name}' not in text:
            text += f'\n\n<b>Имя категории:</b>{category_name}\n\n'
            text += f'<b>Категория ID:</b>{category_id}\n'
        text += f'<b>Имя сервера:</b>{server_name} | {server_id}\n' \
                f'<b>Цена:</b>{price}\n'
    await call.message.answer(text)


@dp.callback_query_handler(cb_admin_payment.filter(action='paid_keyboard'))
@dp.callback_query_handler(cb_admin.filter(action='paid_payments'))
async def paid_payments(call:types.CallbackQuery,callback_data:dict):
    await call.answer()
    text = '------Платежи------\n\n'
    MAX_PAYMENTS_PER_MESSAGE = 5

    payments = await payment_table.get_paid_payment(status='paid')
    count_payments = (len(payments))

    if count_payments > 0:
        page = int(callback_data.get('page', 1))  # Получаем страницу
        start_index = (page-1)*MAX_PAYMENTS_PER_MESSAGE
        end_index = start_index+MAX_PAYMENTS_PER_MESSAGE
        payments = payments[start_index:end_index]

        for payment in payments:
            label = payment[0]
            user_id_table = payment[1]
            user_name = await user_table.get_username(user_id_table)
            payment_method = payment[2]
            amount = payment[3]
            time_stamp = payment[4]
            text += f'<code>#{label}\n</code>' \
                    f'<b>Дата:</b>{time_stamp}\n' \
                    f'<b>Пользователь:</b>{user_name}\n' \
                    f'<b>Метод:</b>{payment_method}\n' \
                    f'<b>Сумма:</b>{amount}\n\n'

        await call.message.edit_text(text,reply_markup= await payment_keyboard(page))


@dp.callback_query_handler(cb_admin.filter(action='basket_users'))
async def basket_users_admin(call:types.CallbackQuery,callback_data:dict):
    text = '➖➖➖➖➖Корзины➖➖➖➖➖\n\n'
    await call.answer()

    users_basket = await basket_table.get_users_baskets()
    for basket in users_basket:
        user_name = basket[0]
        count_product = basket[1]
        text += f'<b>Имя:</b>{user_name}\n' \
                f'<b>Кол-во покупок:</b>{count_product}\n\n'

    await call.message.edit_text(text,reply_markup=await back_keyboard())



@dp.callback_query_handler(cb_admin.filter(action='send_message'))
async def send_messages(call:types.CallbackQuery,callback_data:dict):

    await call.message.delete()

    await call.message.answer('Пришлите текст')

    await SendMessage.send_message.set()


@dp.message_handler(state=SendMessage.send_message.state)
async def check_text(message:types.Message,state:FSMContext):
    await message.answer('Вы действительно хотите сделать рассылку с таким текстом\n\n'
                         f'{message.text}',reply_markup=await send_message_kb(message.text))

    await state.reset_state()


@dp.callback_query_handler(cb_admin_send_message.filter(action='send_message_yes'))
async def yes_send_message(call:types.CallbackQuery,callback_data:dict):
    await call.message.delete()
    count_sending = 0
    count_not = 0
    text = callback_data.get('text')
    users = await user_table.get_users()

    message_id = await bot.send_message(chat_id=call.message.chat.id,
                                        text=f'Отправлено {count_sending}\n'
                                             f'Не отправлено {count_not}\n')

    for user in users:
        await asyncio.sleep(1)
        try:
            # await bot.send_message(chat_id=int(user[1]), text=f'{message}')
            # await bot.send_video(chat_id=int(user[1]),video=media,caption=f'{message}')
            await bot.send_message(chat_id=user[1],text=f'<b>{text}</b>')
            count_sending += 1
            await bot.edit_message_text(chat_id=config.ADMIN_ID, message_id=message_id.message_id,
                                        text=f'Кол-во пользователей {len(users)}\n'
                                             f'Отправлено {count_sending}\n'
                                             f'Блок {count_not}\n')

            # await bot.send_message(chat_id=config.ADMIN_ID,
            #                           text=f'Рассылка отправлена пользователю {user[1]},{str(user[2])}')  # user[2]

        except Exception as e:
            print(e, f'{int(user[1])}')
            count_not += 1
            await bot.edit_message_text(chat_id=config.ADMIN_ID, message_id=message_id.message_id,
                                        text=f'Кол-во пользователей {len(users)}\n'
                                             f'Отправлено {count_sending}\n'
                                             f'Блок {count_not}\n')
            # await bot.send_message(chat_id=config.ADMIN_ID, text=f'Пользователь {user[1],{str(user[2])}} заблокировал бота')
    await bot.delete_message(chat_id=call.message.chat.id,message_id=message_id.message_id)
    await bot.send_message(chat_id=config.ADMIN_ID,
                           text='Рассылка завершена\n'
                                f'Отправил {count_sending}\n'
                                f'В блоке {count_not}\n')




##--------------Добавить категорию------------#
#
#@dp.callback_query_handler(cb_admin.filter(action='add_category'))
#async def add_category_btn(call:types.CallbackQuery):
#    text = ''
#    await call.answer()
#    # Тут крч показать какие ID категориев
#    categories = await category_table.get_all_categories()
#    for category in categories:
#        text += f'ID {category[0]} | {category[1]}\n'
#    await call.message.answer(f'Отправьте категорию \n\n'
#                              f'{text}')
#    await AddCategory.send_category.set()
#
#@dp.message_handler(state=AddCategory.send_category.state)
#async def add_categor(message:types.Message,state:FSMContext):
#
#    category_name = message.text
#
#    await category_table.add_category(category_name)
#
#    await message.answer('Категория добавлена')
#    await state.reset_state()



