from sqlalchemy.orm import sessionmaker
from telegram import (InlineKeyboardButton, InlineKeyboardMarkup, 
                   ReplyKeyboardMarkup)

from shop.messages import *
from shop.models import Category, engine, Product


def get_main_menu():
    keyboard = [
        [btn_catalog],
        [btn_cart, btn_help],
        [btn_chat, btn_call]
        ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)





class CartMenu:
    def __init__(self, product, quantity=1):
        self.product = product
        self.quantity = quantity

    @property
    def _btn_get_sum_all(self):
        sum_all = self.product.price * self.quantity
        return f'{str(self.product.price)} * {str(self.quantity)} = {str(sum_all)} руб.'

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


    def cart_ikb(self):
        keyboard = [
            [InlineKeyboardButton(self._btn_get_sum_all, callback_data='nothing')],

            [InlineKeyboardButton(emoji_plus, callback_data='add'),
             InlineKeyboardButton(emoji_minus, callback_data='minus')],

            [InlineKeyboardButton('<<< Назад', callback_data=f'back_to_product_list_{str(self.product.category.id)}')]
            ]
        return InlineKeyboardMarkup(keyboard)



class Menu:
    def __init__(self):
        self.len_one_screen = 5
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
        Session = sessionmaker(bind=engine)
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
            ikb_list.append(InlineKeyboardButton(f'{product.name} {str(product.price)} руб', callback_data=f'prod_{str(product.id)}'))
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
