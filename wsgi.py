import os
import logging
import copy

from ifaxbotcovid.bot import factory
from ifaxbotcovid.config import settings
from ifaxbotcovid.config import startmessage


TOKEN = os.environ.get('TOKEN')
URL = os.environ.get('URL')

app = factory.create_app()
bot, logger = factory.create_bot(
    TOKEN, get_logger=True, loglevel=logging.INFO
)
chef = factory.create_chef(
    short_procedure_key=settings.short_procedure_key,
    check_phrases=settings.key_words,
    stop_phrase=settings.stop_phrase,
    maxlen=3,
    time_gap=1.5
)

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


# storing objects in flask config
app.config['TELEBOT'] = bot
app.config['TELEBOT_LOGGER'] = logger
app.config['BOT_CHEF'] = chef
app.config['TELEBOT_URL'] = URL
app.config['TELEGRAM_TOKEN'] = TOKEN

with app.app_context():

    logger.info('Registering blueprint...')

    # getting and registering routes from blueprint
    from ifaxbotcovid.bot import routes
    app.register_blueprint(routes.main)
