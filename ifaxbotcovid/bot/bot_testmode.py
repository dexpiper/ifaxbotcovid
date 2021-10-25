import logging

from ifaxbotcovid.bot.factory import create_bot, create_chef
import ifaxbotcovid.config.startmessage as startmessage
import ifaxbotcovid.config.settings as settings


try:
    import ifaxbotcovid.config.token as tkn
    TOKEN = tkn.TOKEN
except ImportError or ModuleNotFoundError as err:
    raise err

bot, logger = create_bot(
    TOKEN, get_logger=True, loglevel=logging.INFO
)

chef = create_chef(
    short_procedure_key=settings.short_procedure_key,
    check_phrases=settings.key_words,
    stop_phrase=settings.stop_phrase,
    maxlen=3,
    time_gap=1.5
)


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


def run_long_polling():
    bot.infinity_polling()
