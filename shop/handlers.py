import logging
import re

from sqlalchemy.orm import sessionmaker
from telegram import InlineKeyboardMarkup
from telegram.error import BadRequest
from telegram.ext import ConversationHandler

from shop.keyboard import *
from shop.messages import *
from shop.models import Category, engine, Product, ShoppingCart, User
# from shop.shopping_cart import CartMenu
from shop.keyboard import EditProductMenu, ProductMenu, Menu


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
    del_replykb_messages(update, context)
    query = update.callback_query
    if query:
        chat_id = query.message.chat_id
    else: chat_id = update.message.chat_id

    text = 'Выберите категорию'
    msg_id = context.user_data.get('msg_id')
    if msg_id:
        msg = context.bot.edit_message_text(
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
    product_id = int(query.data.split('_')[-1])

    Session = sessionmaker(bind=engine)
    session = Session()

    product = session.query(Product).filter_by(id=product_id).first()

    if 'prod_edit_' in query.data:
        menu = EditProductMenu(product)
    else:
        menu = ProductMenu(product)

    context.user_data['cart_menu'] = menu
    context.bot.edit_message_text(
        chat_id=query.message.chat_id,
        message_id=context.user_data['msg_id'],
        text=menu.product.text,
        reply_markup=menu.product_ikb
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
        reply_markup=menu.product_ikb
        )


def update_cart(update, context):
    query = update.callback_query
    product_id = int(query.data.split('_')[-1])
    menu = context.user_data['cart_menu']

    Session = sessionmaker(bind=engine)
    session = Session()

    shopping_cart = session.query(ShoppingCart)\
        .filter_by(user_id=query.from_user.id).first()

    if session.query(CartItem).filter_by(product_id=product_id)\
        .count() == 0:
        cart_item = CartItem(
            product_id=product_id,
            quantity=menu.quantity,
            shopping_cart_id=shopping_cart.id
            )
        session.add(cart_item)

    else:
        cart_item = session.query(CartItem)\
            .filter_by(product_id=product_id).first()
        cart_item.quantity = menu.quantity
    session.commit()

    query.answer('Товар добавлен в корзину')

    try:
        context.bot.edit_message_reply_markup(
            chat_id=query.message.chat_id,
            message_id=context.user_data['msg_id'],
            reply_markup=menu.product_ikb
            )
    except BadRequest:
        pass


def show_cart_handl(update, context):
    del_replykb_messages(update, context)
    query = update.callback_query
    if query:
        chat_id = query.message.chat_id
        user_id = query.from_user.id
    else:
        chat_id = update.message.chat_id
        user_id = update.message.from_user.id

    Session = sessionmaker(bind=engine)
    session = Session()

    shopping_cart = session.query(ShoppingCart)\
        .filter_by(user_id=user_id).first()
    text = shopping_cart.show_cart_items(session)

    cart_menu = CartMenu()
    menu = cart_menu.cart_ikb

    # Если корзина пустая
    if not text:
        text = msg_empty_cart
        menu = InlineKeyboardMarkup([[]])

    msg_id = context.user_data.get('msg_id')
    if msg_id:
        msg = context.bot.edit_message_text(
            chat_id=chat_id,
            message_id=msg_id,
            text=text, 
            reply_markup=menu
            )
    else:
        msg = context.bot.send_message(
            chat_id=chat_id,
            text=text,
            reply_markup=menu
            )
    context.user_data['msg_id'] = msg.message_id


def back_to_cart(update, context):
    query = update.callback_query
    chat_id = query.message.chat_id
    user_id = query.from_user.id
    product_id = int(query.data.split('_')[-1])
    menu = context.user_data['cart_menu']

    Session = sessionmaker(bind=engine)
    session = Session()

    cart_item = session.query(CartItem)\
        .filter_by(product_id=product_id).first()
    cart_item.quantity = menu.quantity


    shopping_cart = session.query(ShoppingCart)\
        .filter_by(user_id=user_id).first()
    text = shopping_cart.show_cart_items(session)
    session.commit()

    cart_menu = CartMenu()
    menu = cart_menu.cart_ikb

    # Если корзина пустая
    if not text:
        text = msg_empty_cart
        menu = InlineKeyboardMarkup([[]])

    msg_id = context.user_data.get('msg_id')
    if msg_id:
        msg = context.bot.edit_message_text(
            chat_id=chat_id,
            message_id=msg_id,
            text=text, 
            reply_markup=menu
            )
    else:
        msg = context.bot.send_message(
            chat_id=chat_id,
            text=text,
            reply_markup=menu
            )
    context.user_data['msg_id'] = msg.message_id


def del_replykb_messages(update, context):
    pattern = f'({btn_catalog}|{btn_cart}|{btn_help}|\
                {btn_chat}|{btn_call})'

    query = update.callback_query
    if query:
        msg_id = query.message.message_id
        chat_id = query.message.chat_id
        result = re.search(pattern, query.message.text)
    else: 
        msg_id = update.message.message_id
        chat_id = update.message.chat_id
        result = re.search(pattern, update.message.text)

    if not result:
        return

    context.bot.delete_message(
        chat_id=chat_id,
        message_id=msg_id
        )



def delete_product_from_cart(update, context):
    query = update.callback_query
    cart_item_id = int(query.data.split('_')[-1])

    Session = sessionmaker(bind=engine)
    session = Session()
    cart_item = session.query(CartItem).filter_by(id=cart_item_id).first()
    session.delete(cart_item)

    cart_items = cart_item.shopping_cart.cart_items
    menu = get_edit_products_list(cart_items)

    if not menu:
        menu = InlineKeyboardMarkup([[]])
        context.bot.edit_message_text(
            chat_id=query.message.chat_id,
            message_id=context.user_data['msg_id'],
            text=msg_empty_cart,
            reply_markup=menu
            )
        session.commit()
        return

    context.bot.edit_message_text(
        chat_id=query.message.chat_id,
        message_id=context.user_data['msg_id'],
        text=msg_edit_cart,
        reply_markup=menu
        )
    session.commit()


def edit_cart_handler(update, context):
    query = update.callback_query
    user_id = query.from_user.id
    Session = sessionmaker(bind=engine)
    session = Session()

    shopping_cart = session.query(ShoppingCart).filter_by(user_id=user_id)\
        .first()
    menu = get_edit_products_list(shopping_cart.cart_items)
    if not menu:
        context.bot.edit_message_text(
            chat_id=query.message.chat_id,
            message_id=context.user_data['msg_id'],
            text=msg_empty_cart,
            reply_markup=menu
            )
        session.commit()
        return

    context.bot.edit_message_text(
        chat_id=query.message.chat_id,
        message_id=context.user_data['msg_id'],
        text=msg_edit_cart,
        reply_markup=menu
        )
    session.commit()






def checkout_start(update, context):
    query = update.callback_query
    query.message.reply_text(msg_checkout_place)
    return ConversationHandler.END
