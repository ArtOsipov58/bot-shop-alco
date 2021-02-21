btn_catalog = 'Каталог'
btn_cart = 'Корзина'
btn_help = 'Помощь'
btn_chat = 'Онлай-чат'
btn_call = 'Позвонить'

msg_start = '''Вас приветствует бот магазина XXX!
Телефон: +7 (495) 622-11-00 или +7 (967) 233-44-22
Звонки принимаются с 21:00 до 9:00

🎁При заказе через бота действует скидка 10% '''


def msg_cart(product):
    text = f'''Просмотр товара в категории: {product.category.name}

<b>{product.name}</b>

<b>Цена:</b> {str(product.price)} руб.<a href="http://i.imgur.com/I86rTVl.jpg">&#8288;</a>'''
    return text
