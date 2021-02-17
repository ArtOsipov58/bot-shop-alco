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
    subcat_id = Column(Integer, ForeignKey('subcategory.id'))

    subcat_list = relationship('SubCategory', back_populates='category')
    product_list = relationship('Product', back_populates='category')





class SubCategory(Base):
    __tablename__ = 'subcategory'

    id = Column(Integer, primary_key=True)
    name = Column(String(15), nullable=False)
    product_id = Column(Integer, ForeignKey('product.id'))

    category = relationship('Category', back_populates='subcat_list')
    product_list = relationship('Product', back_populates='subcategory')



class Product(Base):
    __tablename__ = 'product'

    id = Column(Integer, primary_key=True)
    name = Column(String(20), nullable=False)

    subcategory = relationship('SubCategory', back_populates='product_list')
    category = relationship('Category', back_populates='product_list')





