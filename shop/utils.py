import os
import sys
parent_dir = os.path.abspath(os.path.dirname(__file__))
sys.path.append(os.path.dirname(parent_dir))


from email.mime.text import MIMEText
from email.header import Header
import smtplib

import pandas as pd
from sqlalchemy.orm import sessionmaker

from shop.models import Category, engine, Product
import config


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
                price=int(float(row['Цена: Цена продажи'].replace(',', '.'))),
                artikul=row['Артикул'],
                cat_id=category.id
                )
            session.add(product)

    session.commit()


def send_email(message, subject):
    msg = MIMEText(message, 'plain', 'utf-8')
    msg['Subject'] = Header(subject, 'utf-8')
    msg['From'] = config.EMAIL_LOGIN
    msg['To'] = config.RECIPIENT_EMAIL

    # s = smtplib.SMTP(config.HOST, 587, timeout=15)
    s = smtplib.SMTP(config.HOST, 465, timeout=15)
    # s.set_debuglevel(1)
    try:
        s.starttls()
        s.login(config.EMAIL_LOGIN, config.EMAIL_PASSWD)
        s.sendmail(msg['From'], config.RECIPIENT_EMAIL, msg.as_string())
    finally:
        s.quit()
