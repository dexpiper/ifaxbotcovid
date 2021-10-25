from flask import Blueprint
from flask import current_app
from flask import request

import telebot


app = current_app

with app.app_context():
    bot = current_app.config['TELEBOT']
    logger = current_app.config['TELEBOT_LOGGER']
    chef = current_app.config['BOT_CHEF']
    URL = current_app.config['TELEBOT_URL']
    TOKEN = current_app.config['TELEGRAM_TOKEN']
    main = Blueprint('main', __name__)


#
# FLASK ROUTES
#
@main.route('/' + TOKEN, methods=['POST'])
def getMessage():
    bot.process_new_updates(
        [telebot.types.Update.de_json(
            request.stream.read().decode("utf-8")
            )]
    )
    return "!", 200


@main.route('/setwebhook', methods=['GET', 'POST'])
def set_webhook():
    bot.remove_webhook()
    s = bot.set_webhook('{URL}{HOOK}'.format(URL=URL, HOOK=TOKEN))
    if s:
        return "webhook setup ok"
    else:
        return "webhook setup failed"


@main.route('/')
def index():
    return '.'
