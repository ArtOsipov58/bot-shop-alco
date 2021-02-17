import os
import sys
parent_dir = os.path.abspath(os.path.dirname(__file__))
sys.path.append(os.path.dirname(parent_dir))




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

    subcat_list = relationship('SubCategory', back_populates='category')

    def __repr__(self):
        return f'<Category {self.name}>'


class SubCategory(Base):
    __tablename__ = 'subcategory'

    id = Column(Integer, primary_key=True)
    name = Column(String(15), nullable=False)
    category_id = Column(Integer, ForeignKey('category.id'))

    category = relationship('Category', back_populates='subcat_list')
    product_list = relationship('Product', back_populates='subcategory')

    def __repr__(self):
        return f'<SubCategory {self.name}>'


class Product(Base):
    __tablename__ = 'product'

    id = Column(Integer, primary_key=True)
    name = Column(String(20), nullable=False)
    price = Column(Integer, nullable=False)
    image = Column(String(50))
    subcat_id = Column(Integer, ForeignKey('subcategory.id'))

    subcategory = relationship(
        'SubCategory', 
        back_populates='product_list'
        )

    def __repr__(self):
        return f'<Product {self.name}>'


class User(Base):
    __tablename__ = 'user'

    user_id = Column(Integer, primary_key=True)
    



class Cart(Base):
    __tablename__ = 'cart'





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