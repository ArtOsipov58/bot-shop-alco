import os
import sys
parent_dir = os.path.abspath(os.path.dirname(__file__))
sys.path.append(os.path.dirname(parent_dir))



from datetime import datetime

from sqlalchemy import (create_engine, Table, Column, Integer, Numeric, 
                        String, DateTime, ForeignKey) 
from sqlalchemy.ext.declarative import declarative_base 
from sqlalchemy.orm import relationship, sessionmaker

Base = declarative_base()
engine = create_engine('sqlite:///base.db')



class Category(Base):
    __tablename__ = 'category'

    id = Column(Integer, primary_key=True)
    name = Column(String(15), nullable=False)
    order = Column(Integer)

    product_list = relationship('Product', back_populates='category')

    def __repr__(self):
        return f'<Category {self.name}>'


class Product(Base):
    __tablename__ = 'product'

    id = Column(Integer, primary_key=True)
    name = Column(String(20), nullable=False)
    price = Column(Integer, nullable=False)
    artikul = Column(String(20), unique=True)
    image = Column(String(50))
    cat_id = Column(Integer, ForeignKey('category.id'))

    category = relationship('Category', back_populates='product_list')
    cart_item = relationship('CatrItem', back_populates='product')

    @property
    def text(self):
        text = f'''Просмотр товара в категории: {self.category.name}

<b>{self.name}</b>

<b>Цена:</b> {str(self.price)} руб.<a href="http://i.imgur.com/I86rTVl.jpg">&#8288;</a>'''
        return text


    # def get_sum_all(self):
    #     text = f''
    #     return self.price * self.cart_item.quantity






    def __repr__(self):
        return f'<Product {self.name}>'


class User(Base):
    __tablename__ = 'user'

    user_id = Column(Integer, primary_key=True)
    first_name = Column(String(15), nullable=False)
    phone = Column(String(15))

    shopping_cart = relationship('ShoppingCart', back_populates='user')

    def __repr__(self):
        return f'<User id={str(self.id)}, name={self.first_name}>'


class ShoppingCart(Base):
    __tablename__ = 'shopping_cart'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.user_id'), unique=True)
    created_date = Column(DateTime, default=datetime.now())

    cart_items = relationship('CatrItem', back_populates='shopping_cart')
    user = relationship('User', back_populates='shopping_cart')


class CatrItem(Base):
    __tablename__ = 'cart_items'

    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey('product.id'))
    quantity = Column(Integer)
    created_date = Column(DateTime, default=datetime.now())
    shopping_cart_id = Column(Integer, ForeignKey('shopping_cart.id'))

    shopping_cart = relationship('ShoppingCart', back_populates='cart_items')
    product = relationship('Product', back_populates='cart_item')











# Base.metadata.create_all(engine)

# Session = sessionmaker(bind=engine)
# session =Session()

# add_cat
# subcat = SubCategory(name='Обувь')
# session.add(category)
# session.commit()


# product = session.query(Product).filter_by(id=1).first()
# print(product.category)

# product = Product(
#     name='Трусы Улица Сезам', 
#     price=100,
#     image='1.jpg',
#     subcat_id=2)

# session.add(product)
# session.commit()