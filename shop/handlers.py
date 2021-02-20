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
    update.message.reply_text(
        'Выберите категорию',
        reply_markup=get_cat_ikb())


def select_product(update, context):
    query = update.callback_query
    Session = sessionmaker(bind=engine)
    session = Session()
    # product = session.query(Product).filter_by(cat_id=int(query.data.split('_')[-1])).all()
    category = session.query(Category).filter_by(id=int(query.data.split('_')[-1])).first()
    query.message.reply_text(
        f'Категория: <b>{category.name}</b>',
        reply_markup=get_product_ikb(category.product_list)
        )


def get_product_cart(update, context):
    query = update.callback_query
    query.message.reply_text('Вот карточка товара')