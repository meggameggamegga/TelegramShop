from environs import Env

env = Env()
env.read_env()

BOT_TOKEN = env.str('TOKEN_ID')
ADMIN_ID = env.str('ADMIN_ID')
CHAT_ID = env.str('CHAT_ID')

CRYPTOBOT_TOKEN = env.str('CRYPTOBOT_TOKEN')

YOOMONEY_TOKEN = env.str('YOOMONEY_TOKEN')
YOOMONEY_CARD = env.str('YOOMONEY_CARD')

CRYSTALPAY_LOGIN = env.str('CRYSTALPAY_LOGIN')
CRYSTALPAY_SECRET = env.str('CRYSTALPAY_SECRET')

ORDERS_PATH = 'orders'

# CHAT_ID = env.str('CHAT_ID')

START_MESSAGE = '<b>Приветствую вас в шопе по продаже аккаунтов Valorant!\n\n' \
                '🎮 Здесь вас ждут только отличные игровые аккаунты💰</b>'

CATEGORY_BTN = '📦Категории'
AMOUNT_BTN = '💰Наличие'
RULES_BTN = '📝Правила'
SUPPORT_BTN = '👨‍💻Поддержка'
PROFILE_BTN = '👤Профиль'

PRODUCT_MESSAGE = '💰 Цена: 40 ₽\n' \
                  '📃 Описание: [RU]' \
                  '✨ После покупки Вы получаете рандомный  Valorant аккаунт.' \
                  'Скины и агенты - не проверялись. Доступ к почте так же не проверялись. Гарантированный вход через лаунчер.\n' \
                  'Через сайт на аккаунт зайти не получится.\n' \
                  'Гарантия: на момент входа\n' \
                  '✨Формат выдачи: лог:пасс\n'

PRE_PAYMENT_MESSAGE = f'📃 Товар:\n' \
                      f'💰 Цена:\n' \
                      f'📦 Кол-во:\n' \
                      f'💡 Заказ:\n' \
                      f'🕐 Время заказа:\n' \
                      f'Итоговая сумма:\n' \
                      f'💲 Способ оплаты:\n'

RULES_MESSAGE = '<b>Незнание правил не освобождает от ответственности.' \
                'Сделав покупку в боте' \
                'вы автоматически соглашаетесь с правилами нижие.</b>\n\n' \
                '1.Гарантия аккаунта на момент покупки\n' \
                '2.За выдачу невалидного аккаунта средства возвращаются на баланс бота\n' \
                '3.Получить автоматическую замену можно в профиле\n' \
                '4.Если был осуществлён перевод на неправильные реквизиты, возврат средств не предусмотрен.\n'
