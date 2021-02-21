import logging

from sqlalchemy.orm import sessionmaker

from shop.keyboard import *
from shop.models import Category, engine, Product


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
    msg = update.message.reply_text(
        'Выберите категорию',
        reply_markup=menu.get_cat_ikb()
        )
    context.user_data['msg_id'] = msg.message_id


def get_cat_list(update, context):
    query = update.callback_query
    cat_id = int(query.data.split('_')[-1])
    Session = sessionmaker(bind=engine)
    session = Session()
    category = session.query(Category).filter_by(id=cat_id).first()
    context.user_data['cat_id'] = cat_id

    context.bot.edit_message_text(
        chat_id=query.message.chat_id,
        message_id=context.user_data['msg_id'],
        text=f'Категория: <b>{category.name}</b>',
        reply_markup=menu.get_product_ikb(category.product_list)
        )


def select_product(update, context):
    query = update.callback_query
    screen_num = int(query.data.split('_')[-1])
    Session = sessionmaker(bind=engine)
    session = Session()

    cat_id = context.user_data['cat_id']
    category = session.query(Category).filter_by(id=cat_id).first()
    context.bot.edit_message_text(
        chat_id=query.message.chat_id,
        message_id=context.user_data['msg_id'],
        text=f'Категория: <b>{category.name}</b>',
        reply_markup=menu.get_product_ikb(category.product_list, screen_num=screen_num)
        )


def get_product_cart(update, context):
    query = update.callback_query
    context.bot.edit_message_text(
        chat_id=query.message.chat_id,
        message_id=context.user_data['msg_id'],
        text='Вот карточка товара'
        )
