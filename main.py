import asyncio
import logging
from datetime import datetime, timedelta

from aiogram import Bot,Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.utils import executor

import config
from db.database import DataBase
from db.payment_db import PaymentTable
from db.product_db import ProductTable
from src.utils import task_check_payment

bot = Bot(config.BOT_TOKEN,parse_mode='HTML')
storage = MemoryStorage()
dp = Dispatcher(bot,storage=storage)


def init_logger(name):
    logger = logging.getLogger(name)
    FORMAT = logging.Formatter('%(asctime)s-%(name)s:%(lineno)s-%(levelname)s-%(message)s')
    logger.setLevel(logging.DEBUG)
    sh = logging.StreamHandler()
    sh.setFormatter(FORMAT)
    fh = logging.FileHandler(filename='logs.log',encoding='UTF8')
    fh.setFormatter(FORMAT)#
    fh.setLevel(logging.DEBUG)
    logger.addHandler(sh)
    logger.addHandler(fh)
    logger.debug('Логгер успешно установлен')



logger = logging.getLogger('app.main')

payment_table = PaymentTable('database.db')
user_table = DataBase('database.db')
product_table = ProductTable('database.db')


async def on_startup(_):
    from db.database import DataBase
    asyncio.create_task(task_check_payment(bot))
    data = DataBase('database.db')
    await data.create_tables()
    await bot.send_message(config.ADMIN_ID,'Бот запустился')
    logger.info('Бот запущен')





if __name__ == '__main__':
    from handlers import dp
    #dp.middleware.setup(ChannelMiddleware(bot))
    init_logger('app')
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)


