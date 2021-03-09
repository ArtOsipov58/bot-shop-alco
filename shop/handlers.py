from datetime import timedelta
import logging
import os
import re
import requests
import traceback

from sqlalchemy.orm import sessionmaker
from telegram import InlineKeyboardMarkup
from telegram.error import BadRequest

from config import ENGINE, IMAGES_BASE_URL
from shop.keyboard import *
from shop.messages import *
from shop.models import CartItem, Order, Product, ShoppingCart, User
from shop.keyboard import EditProductMenu, ProductMenu, Menu
from shop.utils import import_price, send_email


logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(funcName)s - %(message)s',
    level = logging.INFO,
    filename = 'log.log'
    )


def start(update, context):
    user_id = update.message.from_user.id
    Session = sessionmaker(bind=ENGINE)
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

    msg = update.message.reply_text(
        msg_start,
        reply_markup=get_main_menu()
        )
    context.user_data['main_menu_msg_id'] = msg.message_id


def main_menu_handl(update, context):
    send_reply_msg(
        update, context, 'Главное меню', 
        menu=get_main_menu()
        )


def main_menu_after_change(update, context):
    ''' 
    Переходит в главное меню после того, как 
    клавиатура менялась
    '''

    main_menu_msg_id = context.user_data.get('main_menu_msg_id')
    if main_menu_msg_id:
        # Удаляем сообщение с основным меню
        context.bot.delete_message(
            chat_id=update.message.chat_id,
            message_id=main_menu_msg_id
            )

    # Заменяем его таким же сообщением, с главным меню
    msg = context.bot.send_message(
        chat_id=update.message.chat_id,
        text=msg_start,
        reply_markup=get_main_menu()
        )
    context.user_data['main_menu_msg_id'] = msg.message_id
    send_reply_msg(update, context, msg_main_menu)


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

    send_reply_msg(update, context, text, menu=menu.get_cat_ikb())




def get_products_list(update, context):
    ''' 
    Получаем список продуктов
    '''
    query = update.callback_query
    cat_id = int(query.data.split('_')[-1])
    Session = sessionmaker(bind=ENGINE)
    session = Session()
    product_list = session.query(Product).filter_by(cat_id=cat_id)\
        .order_by(Product.price).all()
    context.user_data['cat_id'] = cat_id

    product_menu = Menu()
    context.bot.edit_message_text(
        chat_id=query.message.chat_id,
        message_id=context.user_data['msg_id'],
        text=f'Категория: <b>{product_list[0].category.name}</b>',
        reply_markup=product_menu.get_product_ikb(product_list)
        )


def navigate_in_category(update, context):
    ''' 
    Когда нажали кнопки <<< >>>
    '''
    query = update.callback_query
    screen_num = int(query.data.split('_')[-1])
    Session = sessionmaker(bind=ENGINE)
    session = Session()

    cat_id = context.user_data['cat_id']
    product_list = session.query(Product).filter_by(cat_id=cat_id)\
        .order_by(Product.price).all()

    product_menu = Menu()
    context.bot.edit_message_text(
        chat_id=query.message.chat_id,
        message_id=context.user_data['msg_id'],
        text=f'Категория: <b>{product_list[0].category.name}</b>',
        reply_markup=product_menu.get_product_ikb(product_list, screen_num=screen_num)
        )


def get_product_cart(update, context):
    query = update.callback_query
    product_id = int(query.data.split('_')[-1])

    Session = sessionmaker(bind=ENGINE)
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

    Session = sessionmaker(bind=ENGINE)
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
        user_id = query.from_user.id
    else: user_id = update.message.from_user.id

    Session = sessionmaker(bind=ENGINE)
    session = Session()

    shopping_cart = session.query(ShoppingCart)\
        .filter_by(user_id=user_id).first()
    text = shopping_cart.show_cart_items

    cart_menu = CartMenu()
    menu = cart_menu.cart_ikb

    # Если корзина пустая
    if not text:
        text = msg_empty_cart
        menu = InlineKeyboardMarkup([[]])

    send_reply_msg(update, context, text, menu=menu)


def send_reply_msg(update, context, text, menu=None, main_menu=False):
    del_replykb_messages(update, context)
    query = update.callback_query
    if query:
        chat_id = query.message.chat_id
    else: chat_id = update.message.chat_id

    if not menu:
        menu = InlineKeyboardMarkup([[]])

    msg_id = context.user_data.get('msg_id')
    if msg_id:
        try:
            msg = context.bot.edit_message_text(
                chat_id=chat_id,
                message_id=msg_id,
                text=text, 
                reply_markup=menu
                )
        except BadRequest:
            # Возникает, когда пытается редактировать 
            # сообщение с reply-клавиатурой

            # Удаляем предыдущее собщение
            try:
                context.bot.delete_message(
                    chat_id=chat_id,
                    message_id=msg_id
                    )
            except BadRequest:
                pass

            # Шлём основное сообщение
            msg = context.bot.send_message(
                chat_id=chat_id,
                text=text,
                reply_markup=menu
                )
            context.user_data['msg_id'] = msg.message_id

    else:
        try:
            msg = context.bot.send_message(
                chat_id=chat_id,
                text=text,
                reply_markup=menu
                )
            context.user_data['msg_id'] = msg.message_id
        except BadRequest:
            pass


def back_to_cart(update, context):
    query = update.callback_query
    chat_id = query.message.chat_id
    user_id = query.from_user.id
    product_id = int(query.data.split('_')[-1])
    menu = context.user_data['cart_menu']

    Session = sessionmaker(bind=ENGINE)
    session = Session()

    cart_item = session.query(CartItem)\
        .filter_by(product_id=product_id).first()
    cart_item.quantity = menu.quantity


    shopping_cart = session.query(ShoppingCart)\
        .filter_by(user_id=user_id).first()
    text = shopping_cart.show_cart_items
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
    '''
    Удаляем сообщения от репли клавиатуры
    '''
    pattern = f'({btn_catalog}|{btn_cart}|{btn_help}|'\
              f'{btn_chat}|{btn_call}|{btn_back_to_main_menu})'

    query = update.callback_query
    if query:
        msg_id = query.message.message_id
        chat_id = query.message.chat_id
        result = re.search(pattern, query.message.text)
    else: 
        msg_id = update.message.message_id
        chat_id = update.message.chat_id
        try:
            result = re.search(pattern, update.message.text)
        except TypeError:
            result = 'contact'

    if not result:
        return

    try:
        context.bot.delete_message(
            chat_id=chat_id,
            message_id=msg_id
            )
    except BadRequest:
        pass


def delete_product_from_cart(update, context):
    query = update.callback_query
    cart_item_id = int(query.data.split('_')[-1])

    Session = sessionmaker(bind=ENGINE)
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
    Session = sessionmaker(bind=ENGINE)
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


def call(update, context):
    send_reply_msg(update, context, msg_call)


def help_handler(update, context):
    send_reply_msg(update, context, msg_help)


def chat_handler(update, context):
    send_reply_msg(update, context, msg_chat_jivo)


def checkout(update, context):
    ''' 
    Нажал "Оформить заказ"
    '''
    query = update.callback_query
    chat_id = query.message.chat_id
    context.user_data['checkout_msg_id'] = context.user_data['msg_id']

    # Удаляем кнопки в сообщении с содержимым корзины
    context.bot.edit_message_reply_markup(
        chat_id=chat_id,
        message_id=context.user_data['checkout_msg_id']
        )

    msg = context.bot.send_message(
        chat_id=chat_id,
        text=msg_send_phone,
        reply_markup=send_phone_kb()
        )
    context.user_data['msg_id'] = msg.message_id


def get_phone(update, context):
    user_id = update.message.from_user.id
    Session = sessionmaker(bind=ENGINE)
    session = Session()
    user = session.query(User).filter_by(user_id=user_id).first()


    import ipdb; ipdb.set_trace()


    contact = update.message.contact
    if contact:
        phone = contact.phone_number
        user.phone = phone
    else:
        phone = update.message.text

        # Если телефон валидный, то записываем его в базу
        pattern = '((8|\+7|7)[\- ]??(\(?\d{3}\)?[\- ]?)?[\d\- ]{7,15})'
        result = re.search(pattern, phone)
        if result:
            user.phone = result.group(0).strip()

    main_menu_msg_id = context.user_data.get('main_menu_msg_id')
    if main_menu_msg_id:
        # Удаляем сообщение с основным меню
        context.bot.delete_message(
            chat_id=update.message.chat_id,
            message_id=main_menu_msg_id
            )

    # Удаляем сообщение в котором пользователь ввёл телефон
    try:
        context.bot.delete_message(
            chat_id=update.message.chat_id,
            message_id=update.message.message_id
            )
    except BadRequest:
        pass

    # Удаляем сообщение с корзиной
    try:
        context.bot.delete_message(
            chat_id=update.message.chat_id,
            message_id=context.user_data['checkout_msg_id']
            )
    except BadRequest:
        pass

    # Заменяем его таким же сообщением, с главным меню
    msg = context.bot.send_message(
        chat_id=update.message.chat_id,
        text=msg_start,
        reply_markup=get_main_menu()
        )
    context.user_data['main_menu_msg_id'] = msg.message_id

    send_reply_msg(update, context, msg_success)

    order = Order(user_id=user_id)
    session.add(order)

    # Обнуляем корзину после оформления заказа
    for cart_item in user.shopping_cart[-1].cart_items:
        order.product_list.append(cart_item.product)
        session.delete(cart_item)

    msg = msg_new_order(user, order)
    send_email(msg, f'Новый заказ №{str(order.id)}')

    session.commit()


def price_handler(update, context):
    # Скачиваем прайс в текущую директорию
    document = update.message.document
    f = context.bot.get_file(document.file_id)
    price_path = os.path.join(os.getcwd(), 'price.xlsx')
    if os.path.exists(price_path):
        os.remove(price_path)
    f.download(price_path)

    try:
        import_price(price_path)
    except Exception:
        update.message.reply_text('Возникла ошибка при импорте прайса, детали в логе на сервере')
        logging.info(str(traceback.format_exc()))
        return
    update.message.reply_text('Прайс успешно импортирован')


def setup_job(update, context):
    context.job_queue.run_once(
        update_all_photos,
        timedelta(seconds=1),
        context=update.message.chat_id
        )
    update.message.reply_text('Обновление фото началось...')


def update_all_photos(context):
    logging.info('Запускаем обновление всех фото')
    job = context.job
    Session = sessionmaker(bind=ENGINE)
    session = Session()
    for product in session.query(Product):
        url = IMAGES_BASE_URL + product.image
        try:
            resp = requests.get(url)
            resp.raise_for_status()
        except requests.RequestException:
            product.image = 'zaglushka.jpg'
            session.commit()

    context.bot.send_message(
        chat_id=job.context,
        text='Обновление фото завершено')
    logging.info('Обновили все фото')


def check_photo(context):
    Session = sessionmaker(bind=ENGINE)
    session = Session()
    for product in session.query(Product).filter_by(image='zaglushka.jpg'):
        image_file = str(product.artikul) + '.jpg'
        url = IMAGES_BASE_URL + image_file
        try:
            resp = requests.get(url)
            resp.raise_for_status()
            product.image = image_file
            session.commit()

        except requests.RequestException:
            pass
    logging.info('Сделали регулярную проверку всех фото')
