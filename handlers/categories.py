import logging

from aiogram.dispatcher.filters import Command
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import ContentType

import config

from db.category_db import CategoryTable
from db.product_db import ProductTable
from db.server_db import ServerTable
from db.basket_db import BasketTable
from db.database import DataBase

from keyboards.inline_category import cb_server, category_inline, cb_category
from main import bot,dp
from keyboards.menu_start import menu_kb

category_table = CategoryTable('database.db')
product_table = ProductTable('database.db')
server_table = ServerTable('database.db')
basket_table = BasketTable('database.db')

logger = logging.getLogger('app.categories')

@dp.callback_query_handler(cb_category.filter(action='back'))
@dp.callback_query_handler(cb_server.filter(action='servers'))
async def category_server_cb(call:types.CallbackQuery,callback_data:dict):
    logger.info(f'Функция category_server_cb {call.message.chat.first_name}')
    server_id = callback_data.get('server')

    server_name = await server_table.get_server_name(server_id=server_id)
    categories_skins = await category_table.get_all_categories()

    #count_category = product_table.get_count_product(server_id=server_id)

    await call.message.delete()
    await call.message.answer(f'<b>➖➖➖➖➖Категории скинов {server_name}➖➖➖➖➖</b>',reply_markup= await category_inline(categories_skins,server_id))


