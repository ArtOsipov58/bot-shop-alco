import os

from email.mime.text import MIMEText
from email.header import Header
import smtplib

import pandas as pd
from sqlalchemy.orm import sessionmaker

from shop.models import Category, Product
import config


def import_price(price_path):
    Session = sessionmaker(bind=config.ENGINE)
    session = Session()

    exclude_cat_list = ['Хозтовары', 'Доставка']

    # Добавляем новые категории (если есть)
    df = pd.read_excel(price_path)
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

        # Если товара нет в базе
        query = session.query(Product).filter_by(artikul=int(row['Артикул']))
        if query.count() == 0:
            category = session.query(Category).filter_by(
                name=row['Группы']
                ).first()
            product = Product(
                name=row['Наименование'],
                price=int(float(row['Цена: Цена продажи'].replace(',', '.'))),
                artikul=int(row['Артикул']),
                image=str(int(row['Артикул'])) + '.jpg',
                cat_id=category.id
                )
            session.add(product)
        else:
            # Если товар есть в базе, то обновляем инфу
            product = query.first()
            product.name = row['Наименование']
            product.price = int(
                float(row['Цена: Цена продажи'].replace(',', '.'))
                )
            product.image = str(int(row['Артикул'])) + '.jpg'

    set_category_order(session)
    session.commit()


def send_email(message, subject):
    msg = MIMEText(message, 'plain', 'utf-8')
    msg['Subject'] = Header(subject, 'utf-8')
    msg['From'] = os.environ.get('EMAIL_LOGIN')
    msg['To'] = os.environ.get('RECIPIENT_EMAIL')

    s = smtplib.SMTP(os.environ.get('HOST'), 
                     os.environ.get('PORT'), 
                     timeout=10)

    try:
        s.starttls()
        s.login(os.environ.get('EMAIL_LOGIN'), os.environ.get('EMAIL_PASSWD'))
        s.sendmail(msg['From'], 
                   os.environ.get('RECIPIENT_EMAIL'), 
                   msg.as_string())
    finally:
        s.quit()


def set_category_order(session):
    for category in session.query(Category):
        if category.name == 'Виски':
            category.order = 1
        elif category.name == 'Водка':
            category.order = 2
        elif category.name == 'Пиво':
            category.order = 3
        elif category.name == 'Вино':
            category.order = 4
        elif category.name == 'Коньяк':
            category.order = 5
        elif category.name == 'Ром':
            category.order = 6
        elif category.name == 'Шампанское':
            category.order = 7
        elif category.name == 'Вермут':
            category.order = 8
        elif category.name == 'Текила':
            category.order = 9
        elif category.name == 'Ликер':
            category.order = 10
        elif category.name == 'Джин':
            category.order = 11
        elif category.name == 'Нужное':
            category.order = 12
        elif category.name == 'Закуски':
            category.order = 13
        elif category.name == 'Напитки':
            category.order = 14
        elif category.name == 'Сигареты':
            category.order = 15
    session.commit()
