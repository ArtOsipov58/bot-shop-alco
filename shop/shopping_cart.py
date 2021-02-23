import os
import sys
parent_dir = os.path.abspath(os.path.dirname(__file__))
sys.path.append(os.path.dirname(parent_dir))

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from shop.models import ShoppingCart


class Cart:
    def __init__(self, session):
        self.product = product

    @property
    def text(self):
        text = f'''Просмотр товара в категории: {self.product.category.name}

<b>{self.product.name}</b>

<b>Цена:</b> {str(self.product.price)} руб.<a href="http://i.imgur.com/I86rTVl.jpg">&#8288;</a>'''
        return text


    def btn_sum_all(self):
        self.product.cart_items






    def get_menu(self):
        keyboard = [
            [self.btn_sum_all]
            ]



