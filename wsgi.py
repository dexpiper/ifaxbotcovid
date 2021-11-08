import logging
import os
from logging.config import fileConfig

import telebot
from flask import request

from ifaxbotcovid.bot import factory
from ifaxbotcovid.config import settings, startmessage
from ifaxbotcovid.bot.utils import Sender


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


#
# MESSAGE HANDLERS
#
@bot.message_handler(commands=['start'])
def answer_start(message):
    '''
    Bot sends welcome message
    '''
    bot.send_message(message.chat.id, startmessage.startmsg(),
                     parse_mode='HTML')
    botlogger.info(
        'User %s issued "start" command' % message.from_user.username)
    user = message.from_user.username
    chat_id = message.chat.id
    if (user, chat_id) not in settings.users:
        settings.users.append((user, chat_id))


@bot.message_handler(commands=['log'])
def syslog_sender(message):
    '''
    Bot sends system log as a file (admin only)
    '''
    user = message.from_user.username
    chat_id = message.chat.id
    botlogger.info('User %s requested "log" file via command' % user)
    if chat_id in settings.admins:
        botlogger.debug('Admin privileges grunted')
        try:
            bot.send_document(
                message.chat.id, open('botlog.log'), 'document'
            )
        except Exception as exc:
            botlogger.error('No system log file found! Exception: %s' % exc)
    else:
        botlogger.warning('Access to user %s denied' % user)
        bot.send_message(
            message.chat.id, '<b>Access denied</b>', parse_mode='HTML'
        )


@bot.message_handler(content_types=['text'])
def user_request(message):
    botlogger.info('User %s send some text' % message.from_user.username)
    if message.text.lower().endswith('йййй'):
        botlogger.info(
            'User %s requested answer in file' % message.from_user.username
        )
        asfile = True
    else:
        asfile = False
    answer = chef.process_new_message(message=message, asfile=asfile)
    if answer.flag:
        sender = Sender(bot, message, answer, logger=botlogger)
        if asfile:
            botlogger.info('Sending answer in file')
            sender.send_asfile()
        elif len(answer.ready_text) > 4070:
            botlogger.info(
                'Sending answer in file: len answer (%s) > 4070' % str(
                    len(answer.ready_text)
                )
            )
            sender.send_asfile()
        else:
            botlogger.info('Sending answer in a direct message')
            sender.send_directly()


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
