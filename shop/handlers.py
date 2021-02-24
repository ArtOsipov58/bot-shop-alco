import logging

from sqlalchemy.orm import sessionmaker

from shop.keyboard import *
from shop.models import Category, engine, Product, ShoppingCart, User
# from shop.shopping_cart import CartMenu
from shop.keyboard import CartMenu, Menu


logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(funcName)s - %(message)s',
    level = logging.INFO,
    filename = 'log.log'
    )


def start(update, context):
    user_id = update.message.from_user.id
    Session = sessionmaker(bind=engine)
    session = Session()
    if session.query(User).filter_by(user_id=user_id).count() == 0:
        user = User(
            user_id=user_id,
            first_name=update.message.from_user.first_name
            )
        session.add(user)
        shopping_cart = ShoppingCart(user_id=user_id)
        session.add(shopping_cart)

    session.commit()

    update.message.reply_text(
        msg_start,
        reply_markup=get_main_menu()
        )


def get_my_id(update, context):
    user_id = update.message.from_user.id
    update.message.reply_text(f'Ваш user_id: {str(user_id)}')
    logging.info(f'user_id клиента: {str(user_id)}')


def select_category(update, context):
    query = update.callback_query
    if query:
        chat_id = query.message.chat_id
    else: chat_id = update.message.chat_id

    text = 'Выберите категорию'
    msg_id = context.user_data.get('msg_id')
    if msg_id:
        context.bot.edit_message_text(
            chat_id=chat_id,
            message_id=msg_id,
            text=text,
            reply_markup=menu.get_cat_ikb()
            )
    else:
        msg = context.bot.send_message(
            chat_id=chat_id,
            text=text,
            reply_markup=menu.get_cat_ikb()
            )
    context.user_data['msg_id'] = msg.message_id


def get_products_list(update, context):
    ''' 
    Получаем список продуктов
    '''
    query = update.callback_query
    cat_id = int(query.data.split('_')[-1])
    Session = sessionmaker(bind=engine)
    session = Session()
    category = session.query(Category).filter_by(id=cat_id).first()
    context.user_data['cat_id'] = cat_id

    product_menu = Menu()
    context.bot.edit_message_text(
        chat_id=query.message.chat_id,
        message_id=context.user_data['msg_id'],
        text=f'Категория: <b>{category.name}</b>',
        reply_markup=product_menu.get_product_ikb(category.product_list)
        )


def navigate_in_category(update, context):
    ''' 
    Когда нажали кнопки <<< >>>
    '''
    query = update.callback_query
    screen_num = int(query.data.split('_')[-1])
    Session = sessionmaker(bind=engine)
    session = Session()

    cat_id = context.user_data['cat_id']
    category = session.query(Category).filter_by(id=cat_id).first()

    product_menu = Menu()
    context.bot.edit_message_text(
        chat_id=query.message.chat_id,
        message_id=context.user_data['msg_id'],
        text=f'Категория: <b>{category.name}</b>',
        reply_markup=product_menu.get_product_ikb(category.product_list, screen_num=screen_num)
        )


def get_product_cart(update, context):
    query = update.callback_query
    user_id = query.from_user.id
    product_id = int(query.data.split('_')[-1])

    Session = sessionmaker(bind=engine)
    session = Session()

    menu = CartMenu(session, product_id, user_id)
    context.user_data['cart_menu'] = menu
    context.bot.edit_message_text(
        chat_id=query.message.chat_id,
        message_id=context.user_data['msg_id'],
        text=menu.product.text,
        reply_markup=menu.cart_ikb()
        )


def quantity_handler(update, context):
    query = update. callback_query
    menu = context.user_data['cart_menu']

    if query.data == 'add':
        menu.add
    elif query.data == 'minus':
        result = menu.minus
        if not result:
            query.answer(text='В корзине должен быть хотя бы один товар')

    context.bot.edit_message_reply_markup(
        chat_id=query.message.chat_id,
        message_id=context.user_data['msg_id'],
        reply_markup=menu.cart_ikb()
        )


def add_to_cart(update, context):
    query = update.callback_query

    menu = context.user_data['cart_menu']
    menu.add_to_cart
    query.answer('Товар добавлен в корзину')

    context.bot.edit_message_reply_markup(
        chat_id=query.message.chat_id,
        message_id=context.user_data['msg_id'],
        reply_markup=menu.cart_ikb()
        )


def show_cart_handl(update, context):
    menu = context.user_data.get('cart_menu')
    if not menu:
        Session = sessionmaker(bind=engine)
        session = Session()
        menu = CartMenu(session, product_id, user_id)
    update.message.reply_text(menu.show_cart_items)
