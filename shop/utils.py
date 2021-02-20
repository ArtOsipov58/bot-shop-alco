import os
import sys
parent_dir = os.path.abspath(os.path.dirname(__file__))
sys.path.append(os.path.dirname(parent_dir))



import pandas as pd

from sqlalchemy.orm import sessionmaker

from shop.models import Category, engine, Product


def import_price():
    Session = sessionmaker(bind=engine)
    session = Session()

    exclude_cat_list = ['Хозтовары', 'Доставка']

    # Добавляем новые категории (если есть)
    df = pd.read_excel('НОВАЯ выгрузка.xlsx')
    for index, row in df.iterrows():
        if row['Архивный'] == 'да':
            continue

        if row['Группы'] in exclude_cat_list:
            continue

        if 'Нужное/' in row['Группы']:
            row['Группы'] = row['Группы'].replace('Нужное/', '')

        if session.query(Category).filter_by(name=row['Группы'])\
            .count() == 0:
            category = Category(name=row['Группы'])
            session.add(category)
    session.commit()

    # Добавляем новые товары
    for index, row in df.iterrows():
        if row['Архивный'] == 'да':
            continue
        if row['Группы'] in exclude_cat_list:
            continue

        if 'Нужное/' in row['Группы']:
            row['Группы'] = row['Группы'].replace('Нужное/', '')

        if 'Доставка' in row['Наименование']:
            continue

        if session.query(Product).filter_by(artikul=row['Артикул'])\
            .count() == 0:
            category = session.query(Category).filter_by(
                name=row['Группы']
                ).first()
            product = Product(
                name=row['Наименование'],
                price=row['Цена: Цена продажи'],
                artikul=row['Артикул'],
                cat_id=category.id
                )
            session.add(product)

    session.commit()
