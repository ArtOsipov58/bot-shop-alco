import ast
import logging
import os
import pytz
import sys
from threading import Thread

from telegram import ParseMode
from telegram.ext import (CallbackQueryHandler, CommandHandler, 
                          Defaults, Filters, 
                          MessageHandler, Updater)

import config
from shop.handlers import *
from shop.messages import *


logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(funcName)s - %(message)s',
    level=logging.INFO,
    filename='log.log'
    )

aps_logger = logging.getLogger('apscheduler')
aps_logger.setLevel(logging.WARNING)


defaults = Defaults(
    tzinfo=pytz.timezone('Europe/Moscow'), 
    parse_mode=ParseMode.HTML
    )
mybot = Updater(os.environ.get('TOKEN'), defaults=defaults)


def stop_and_restart():
    """
    Gracefully stop the Updater and replace the 
    current process with a new one
    """
    mybot.stop()
    os.execl(sys.executable, sys.executable, *sys.argv)


def restart(update, context):
    update.message.reply_text('Bot is restarting...')
    Thread(target=stop_and_restart).start()


def main():
    logging.info('Бот запускается.')
    dp = mybot.dispatcher

    mybot.job_queue.run_repeating(
        check_photo,
        interval=3600,
        first=600
        )

    TG_ADMIN_LIST = ast.literal_eval(os.environ.get('TG_ADMIN_LIST'))

    dp.add_handler(CommandHandler('r', restart, 
                                  filters=Filters.user(TG_ADMIN_LIST)))
    dp.add_handler(CommandHandler('update_photos', 
                                  setup_job, 
                                  filters=Filters.user(TG_ADMIN_LIST)))
    dp.add_handler(
        MessageHandler(Filters.document & Filters.user(TG_ADMIN_LIST), 
                       price_handler)
        )
    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(CommandHandler('get_id', get_my_id))
    dp.add_handler(MessageHandler(Filters.regex(f'^({btn_catalog})$'), 
                                  select_category))
    dp.add_handler(MessageHandler(Filters.regex(f'^({btn_cart})$'), 
                                  show_cart_handl))
    dp.add_handler(MessageHandler(Filters.regex(f'^({btn_call})$'), call))
    dp.add_handler(MessageHandler(Filters.regex(f'^({btn_help})$'), 
                                  help_handler))
    dp.add_handler(MessageHandler(Filters.regex(f'^({btn_chat})$'), 
                                  chat_handler))
    dp.add_handler(MessageHandler(Filters.regex(f'^({btn_back_to_main_menu})$'),
                                  main_menu_after_change))
    dp.add_handler(
        MessageHandler(Filters.contact | Filters.regex(config.PHONE_PATTERN), 
                       get_phone)
        )
    dp.add_handler(CallbackQueryHandler(show_cart_handl, 
                                        pattern='^do_nothing$'))
    dp.add_handler(CallbackQueryHandler(get_products_list, 
                                        pattern='^cat_\d{1,2}'))
    dp.add_handler(
        CallbackQueryHandler(get_product_cart, 
                             pattern='^(prod_\d{1,2}|prod_edit_\d{1,2})')
        )
    dp.add_handler(CallbackQueryHandler(checkout, pattern='^checkout$'))
    dp.add_handler(CallbackQueryHandler(checkout_from_cart, 
                                        pattern='^checkout_from_cart$'))
    dp.add_handler(CallbackQueryHandler(navigate_in_category, 
                                        pattern='^nav_\d{1,2}'))
    dp.add_handler(CallbackQueryHandler(select_category, 
                                        pattern='^back$'))
    dp.add_handler(
        CallbackQueryHandler(get_products_list, 
                             pattern='^back_to_product_list_\d{1,2}$')
        )
    dp.add_handler(CallbackQueryHandler(quantity_handler, 
                                        pattern='^(add|minus)$'))
    dp.add_handler(CallbackQueryHandler(update_cart, 
                                        pattern='^update_cart_\d{1,5}'))
    dp.add_handler(
        CallbackQueryHandler(delete_product_from_cart, 
                             pattern='^delete_product_from_cart_\d{1,5}')
        )
    dp.add_handler(CallbackQueryHandler(edit_cart_handler, 
                                        pattern='^(edit_cart)$'))
    dp.add_handler(CallbackQueryHandler(back_to_cart, 
                                        pattern='^back_to_cart_'))
    dp.add_handler(MessageHandler(Filters.text, not_anderstand))

    mybot.start_polling()
    mybot.idle()


if __name__ == '__main__':
    main()
