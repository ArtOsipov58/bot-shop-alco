from sqlalchemy.orm import sessionmaker
from telegram import (InlineKeyboardButton, InlineKeyboardMarkup, 
                   KeyboardButton, ReplyKeyboardMarkup)

from config import ENGINE
from shop.messages import *
from shop.models import Category



def get_main_menu():
    keyboard = [
        [btn_catalog],
        [btn_cart, btn_help],
        [btn_chat, btn_call]
        ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


def send_phone_kb():
    keyboard = [
        [KeyboardButton(btn_send_phone, request_contact=True)],
        [btn_back_to_main_menu]
        ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


def get_edit_products_list(cart_items):
    keyboard = list()
    for cart_item in cart_items:
        btn = f'{cart_item.product.name} ({str(cart_item.quantity)})'
        keyboard.append(
            [InlineKeyboardButton(btn, callback_data=f'prod_edit_{str(cart_item.product.id)}')])
    if not keyboard:
        return False

    keyboard.append([InlineKeyboardButton(btn_do_nothing, callback_data='do_nothing')])
    return InlineKeyboardMarkup(keyboard)


class CartMenu:
    def __init__(self):
        pass

    @property
    def cart_ikb(self):
        keyboard = [
            [InlineKeyboardButton(btn_edit_cart, callback_data='edit_cart'),
             InlineKeyboardButton(btn_checkout, callback_data='checkout')]
             ]
        return InlineKeyboardMarkup(keyboard)



class ProductMenu:
    def __init__(self, product):
        self.product = product
        self.quantity = 1
        self._product_in_cart = False
        if self.product.cart_items:
            self._product_in_cart = True
            self.quantity = self.product.cart_items[0].quantity
            self.cart_item_id = self.product.cart_items[0].id

    @property
    def _btn_get_sum_all(self):
        self.sum_all = self.product.price * self.quantity
        return f'{str(self.product.price)} * {str(self.quantity)} = {str(self.sum_all)} руб.'

    @property
    def add(self):
        self.quantity += 1
        self._btn_get_sum_all

    @property
    def minus(self):
        if self.quantity > 1:
            self.quantity -= 1
            self._btn_get_sum_all
            return True
        else:
            return False

    @property
    def product_ikb(self):
        keyboard = [
            [InlineKeyboardButton(self._btn_get_sum_all, callback_data='nothing')],

            [
             InlineKeyboardButton(emoji_minus, callback_data='minus'),
             InlineKeyboardButton(emoji_plus, callback_data='add')],

             [InlineKeyboardButton(btn_add_to_cart, callback_data=f'update_cart_{str(self.product.id)}')],
             [InlineKeyboardButton(btn_checkout_from_cart, callback_data='checkout_from_cart')],

            [InlineKeyboardButton(btn_back, callback_data=f'back_to_product_list_{str(self.product.category.id)}')]
            ]
        if self._product_in_cart:
            keyboard[1].append(InlineKeyboardButton(btn_delete, callback_data=f'delete_product_from_cart_{str(self.product.cart_items[0].id)}'))
        return InlineKeyboardMarkup(keyboard)


class EditProductMenu(ProductMenu):
    def __init__(self, product):
        ProductMenu.__init__(self, product)

    @property
    def product_ikb(self):
        keyboard = [
            [InlineKeyboardButton(self._btn_get_sum_all, callback_data='nothing')],

            [
             InlineKeyboardButton(emoji_minus, callback_data='minus'),
             InlineKeyboardButton(emoji_plus, callback_data='add')],

             [InlineKeyboardButton(btn_checkout, callback_data='checkout_from_cart')],

             [InlineKeyboardButton(btn_back_to_cart, callback_data=f'back_to_cart_{str(self.product.id)}')]
            ]
        if self._product_in_cart:
            keyboard[1].append(InlineKeyboardButton(btn_delete, callback_data=f'delete_product_from_cart_{str(self.product.cart_items[0].id)}'))
        return InlineKeyboardMarkup(keyboard)




class Menu:
    def __init__(self):
        self.len_one_screen = 100
        self.column_num = 1

    @staticmethod
    def _build_menu(buttons,
                n_cols,
                header_buttons=None,
                footer_buttons=None):
        menu = [buttons[i:i + n_cols] for i in range(0, len(buttons), n_cols)]
        if header_buttons:
            menu.insert(0, [header_buttons])
        if footer_buttons:
            menu.append([footer_buttons])
        return menu

    @staticmethod
    def _split_list(kblist, step):
        result_list = []
        for i in range(step, len(kblist) + step, step):
            if i == step:
                s_list = kblist[:i]
                result_list.append(s_list)
            else:
                split_list = kblist[(i-step) : i]
                result_list.append(split_list)
        return result_list   # Список из списков

    @staticmethod
    def get_cat_ikb():
        Session = sessionmaker(bind=ENGINE)
        session = Session()

        ikb_list = list()
        for cat in session.query(Category).order_by(Category.order):
            ikb_list.append(InlineKeyboardButton(cat.name, callback_data=f'cat_{str(cat.id)}'))
        menu = Menu._build_menu(ikb_list, 3)
        return InlineKeyboardMarkup(menu)


    @staticmethod
    def _get_ikb_list(product_list):
        ikb_list = list()
        for product in product_list:
            ikb_list.append(InlineKeyboardButton(f'{str(product.price)} р. - {product.name}', callback_data=f'prod_{str(product.id)}'))
        return ikb_list

    def get_product_ikb(self, product_list, screen_num=1):
        ikb_list = Menu._get_ikb_list(product_list)
        screen_list = Menu._split_list(ikb_list, self.len_one_screen)
        screen_dict = dict()
        for screen in screen_list:
            screen_dict[str(screen_list.index(screen) + 1)] = screen

        raw_menu = screen_dict[str(screen_num)]
        menu = Menu._build_menu(raw_menu, self.column_num)

        if screen_num == 1:
            if len(screen_list) > 1:
                menu.append([InlineKeyboardButton('>>>', callback_data=f'nav_{str(screen_num+1)}')])
        elif 1 < screen_num < len(screen_dict):

            menu.append(
                [InlineKeyboardButton('<<<', callback_data=f'nav_{str(screen_num-1)}'), 
                 InlineKeyboardButton('>>>', callback_data=f'nav_{str(screen_num+1)}')]
                )
        elif screen_num == len(screen_dict):
            menu.append(
                [InlineKeyboardButton('<<<', callback_data=f'nav_{str(screen_num-1)}')]
                )
        menu.append([InlineKeyboardButton('<<< Назад', callback_data='back')])
        return InlineKeyboardMarkup(menu)



menu = Menu()
