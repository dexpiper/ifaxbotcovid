import logging
import os
from logging.config import fileConfig

import telebot
from flask import request

from ifaxbotcovid.bot import factory
from ifaxbotcovid.config import settings


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
    time_gap=2,
    logger=botlogger
)

# registering into flask
app.config['TELEBOT'] = bot
app.config['TELEBOT_LOGGER'] = tblogger
app.config['COVIDCHEF'] = chef


# registering bot handlers
with app.app_context():

    from ifaxbotcovid.bot.handlers import BotHandlers

    for handler in BotHandlers.handlers:
        name = handler[0]
        kwargs = handler[1]
        bot.register_message_handler(name, **kwargs)


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
