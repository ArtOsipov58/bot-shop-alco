import logging

from shop.keyboard import *


logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(funcName)s - %(message)s',
    level = logging.INFO,
    filename = 'log.log'
    )


def start(update, context):
    update.message.reply_text(
        'Стартовое сообщение...',
        reply_markup=get_main_menu())


def get_my_id(update, context):
    user_id = update.message.from_user.id
    update.message.reply_text(f'Ваш user_id: {str(user_id)}')
    logging.info(f'user_id клиента: {str(user_id)}')


def select_category(update, context):
    update.message.reply_text(
        'Выберите категорию',
        reply_markup=get_cat_ikb())