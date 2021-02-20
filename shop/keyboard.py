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


def get_cat_ikb():
    Session = sessionmaker(bind=engine)
    session = Session()

    ikb_list = list()
    for cat in session.query(Category).order_by(Category.order):
        ikb_list.append(InlineKeyboardButton(cat.name, callback_data=f'cat_{str(cat.id)}'))
    menu = build_menu(ikb_list, 3)
    return InlineKeyboardMarkup(menu)


def get_product_ikb(product_list):
    ikb_list = list()
    for product in product_list:
        ikb_list.append(InlineKeyboardButton(product.name, callback_data=f'prod_{str(product.id)}'))

    menu = build_menu(ikb_list, 2)
    return InlineKeyboardMarkup(menu)



def build_menu(buttons,
            n_cols,
            header_buttons=None,
            footer_buttons=None):
    menu = [buttons[i:i + n_cols] for i in range(0, len(buttons), n_cols)]
    if header_buttons:
        menu.insert(0, [header_buttons])
    if footer_buttons:
        menu.append([footer_buttons])
    return menu



class Menu:

    def build_menu(self, 
                buttons,
                n_cols,
                header_buttons=None,
                footer_buttons=None):
        menu = [buttons[i:i + n_cols] for i in range(0, len(buttons), n_cols)]
        if header_buttons:
            menu.insert(0, [header_buttons])
        if footer_buttons:
            menu.append([footer_buttons])
        return menu



# buttons = []




