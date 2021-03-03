import os
import sys
parent_dir = os.path.abspath(os.path.dirname(__file__))
sys.path.append(os.path.dirname(parent_dir))


from email.mime.text import MIMEText
from email.header import Header
import os
import smtplib

import pandas as pd
from sqlalchemy.orm import sessionmaker

from shop.models import Category, Product
import config


def import_price():
    Session = sessionmaker(bind=config.ENGINE)
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
            product.price = int(float(row['Цена: Цена продажи'].replace(',', '.')))
            product.image = str(int(row['Артикул'])) + '.jpg'

    session.commit()


def send_email(message, subject):
    msg = MIMEText(message, 'plain', 'utf-8')
    msg['Subject'] = Header(subject, 'utf-8')
    msg['From'] = config.EMAIL_LOGIN
    msg['To'] = config.RECIPIENT_EMAIL

    s = smtplib.SMTP(config.HOST, config.PORT, timeout=10)

    try:
        s.starttls()
        s.login(config.EMAIL_LOGIN, config.EMAIL_PASSWD)
        s.sendmail(msg['From'], config.RECIPIENT_EMAIL, msg.as_string())
    finally:
        s.quit()
