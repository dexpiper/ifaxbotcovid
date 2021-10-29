import logging
import os
from logging.config import fileConfig

import telebot
from flask import request

from ifaxbotcovid.bot import factory
from ifaxbotcovid.config import settings, startmessage

# logging settings
fileConfig('ifaxbotcovid/config/logging.ini')
botlogger = logging.getLogger('botlogger')

# getting environ vars
TOKEN = os.environ.get('TOKEN')
URL = os.environ.get('URL')
if TOKEN is None:
    botlogger.warning('TOKEN should be defined as system var')
if URL is None:
    botlogger.warning('URL should be defined as system var')

# creating Flask, Telebot and Chef instances
app = factory.create_app()
bot, tblogger = factory.create_bot(
    TOKEN, get_logger=True, loglevel=logging.INFO
)
chef = factory.create_chef(
    short_procedure_key=settings.short_procedure_key,
    check_phrases=settings.key_words,
    stop_phrase=settings.stop_phrase,
    maxlen=3,
    time_gap=2
)


#
# MESSAGE HANDLERS
#
@bot.message_handler(commands=['start'])
def answer_start(message):
    '''
    Bot sends welcome message
    '''
    bot.send_message(message.chat.id, startmessage.startmsg, parse_mode='HTML')
    botlogger.info(
        'User %s issued "start" command' % message.from_user.username)
    user = message.from_user.username
    chat_id = message.chat.id
    if (user, chat_id) not in settings.users:
        settings.users.append((user, chat_id))


@bot.message_handler(content_types=['text'])
def user_request(message):
    botlogger.info('User %s send some text' % message.from_user.username)
    answer = chef.process_new_message(message)
    if answer.flag:
        if answer.warnmessage:
            bot.send_message(message.chat.id, answer.warnmessage)
            botlogger.info(
                'Warning message sent to %s' % message.from_user.username
            )
        bot.send_message(message.chat.id, answer.ready_text)
        botlogger.info(
            'Ready answer sent to %s' % message.from_user.username
        )
        if message.text.endswith('йй') or message.text.startswith('йй'):
            bot.send_message(message.chat.id, answer.log)
            botlogger.info(
                'Log message sent to %s' % message.from_user.username)


#
# FLASK ROUTES
#
@app.route('/' + TOKEN, methods=['POST'])
def getMessage():
    json_string = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_string)
    app.logger.debug('Get some message')
    bot.process_new_updates([update])
    return "!", 200


@app.route('/setwebhook', methods=['GET', 'POST'])
def set_webhook():
    bot.remove_webhook()
    s = bot.set_webhook('{URL}{HOOK}'.format(URL=URL, HOOK=TOKEN))
    if s:
        app.logger.info('Webhook setup successful')
        return "webhook setup ok"
    else:
        app.logger.critical('Webhook setup failed!')
        return "webhook setup failed"


@app.route('/')
def index():
    app.logger.debug('Operational test. Serving normally')
    return '.'
