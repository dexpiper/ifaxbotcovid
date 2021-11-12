import logging
from logging.config import fileConfig

from ifaxbotcovid.config import settings, startmessage, helpmessage
from ifaxbotcovid.bot.factory import create_bot, create_chef
from ifaxbotcovid.bot.utils import Sender, CommandParser

# logging settings
fileConfig('ifaxbotcovid/config/logging.ini')
botlogger = logging.getLogger('botlogger')
botlogger.setLevel(logging.DEBUG)

try:
    import ifaxbotcovid.config.token as tkn
    TOKEN = tkn.TOKEN
except ImportError or ModuleNotFoundError as err:
    botlogger.warning('File with Telegram token have not been found')
    raise err

bot, tblogger = create_bot(
    TOKEN, get_logger=True, loglevel=logging.INFO
)

chef = create_chef(
    short_procedure_key=settings.short_procedure_key,
    check_phrases=settings.key_words,
    stop_phrase=settings.stop_phrase,
    maxlen=3,
    time_gap=1.5,
    logger=botlogger
)


def run_long_polling():
    botlogger.info('Starting polling...')
    bot.infinity_polling()


#
# Message handlers
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


@bot.message_handler(commands=['help'])
def answer_help(message):
    '''
    Bot sends help message
    '''
    botlogger.info(
        'User %s issued "help" command' % message.from_user.username)
    bot.send_message(message.chat.id, helpmessage.helpmsg(),
                     parse_mode='HTML')


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
    commands = CommandParser.get_settings(message)
    if commands.short:
        botlogger.info(
            'User %s requested a boundary cut' % message.from_user.username
        )
        answer = chef.process_new_message(message=message,
                                          asfile=commands.asfile,
                                          short=commands.short)
    else:
        answer = chef.process_new_message(message=message,
                                          asfile=commands.asfile)
    if answer.flag:
        sender = Sender(bot, message, answer, botlogger,
                        logrequest=commands.logrequest)
        if commands.asfile:
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
