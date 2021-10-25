from flask import Blueprint
from flask import current_app
from flask import request

import telebot

import ifaxbotcovid.config.startmessage as startmessage
import ifaxbotcovid.config.settings as settings


app = current_app

with app.app_context():
    bot = current_app.config['TELEBOT']
    logger = current_app.config['TELEBOT_LOGGER']
    chef = current_app.config['BOT_CHEF']
    URL = current_app.config['TELEBOT_URL']
    TOKEN = current_app.config['TELEGRAM_TOKEN']
    main = Blueprint('main', __name__)


#
# MESSAGE HANDLERS
#
@bot.message_handler(commands=['start'])
def answer_start(message):
    '''
    Bot sends welcome message
    '''
    bot.send_message(message.chat.id, startmessage.s, parse_mode='HTML')
    logger.info(
        'User %s issued "start" command' % message.from_user.username)
    user = message.from_user.username
    chat_id = message.chat.id
    if (user, chat_id) not in settings.users:
        settings.users.append((user, chat_id))


@bot.message_handler(content_types=['text'])
def user_request(message):
    logger.info('User %s send some text' % message.from_user.username)
    answer = chef.process_new_message(message)
    if answer.flag:
        if answer.warnmessage:
            bot.send_message(message.chat.id, answer.warnmessage)
        bot.send_message(message.chat.id, answer.ready_text)
        if message.text.endswith('йй'):
            bot.send_message(message.chat.id, answer.log)


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
