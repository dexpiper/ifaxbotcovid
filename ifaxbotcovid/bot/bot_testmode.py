import logging
from logging.config import fileConfig

from ifaxbotcovid.config import settings, startmessage
from ifaxbotcovid.bot.factory import create_bot, create_chef
from ifaxbotcovid.bot.helpers import FileSaver

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


class Sender:

    def __init__(self, bot, message, answer):
        self.bot = bot
        self.message = message
        self.answer = answer
        self.sign = self._check_if_signed()

    def _check_if_signed(self):
        if (
            self.message.text.endswith('йй')
        ) or (
            self.message.text.startswith('йй')
        ):
            return True
        else:
            return False

    def send_warn(self):
        if self.answer.warnmessage:
            self.bot.send_message(
                self.message.chat.id, self.answer.warnmessage)
            botlogger.info(
                'Warning message sent to %s' % self.message.from_user.username
            )

    def send_log(self):
        if self.sign:
            self.bot.send_message(self.message.chat.id, self.answer.log)
            botlogger.info(
                'Log message sent to %s' % self.message.from_user.username)

    def send_directly(self):
        self.send_warn()
        self.bot.send_message(self.message.chat.id, self.answer.ready_text)
        botlogger.info(
            'Ready answer sent to %s' % self.message.from_user.username
        )
        self.send_log()

    def send_asfile(self):
        path = FileSaver.to_file(
            text=self.answer.ready_text,
            username=self.message.from_user.username
        )
        self.send_warn()
        self.send_log()
        try:
            self.bot.send_document(
                self.message.chat.id, open(path), 'document'
            )
        except Exception as exc:
            botlogger.error('No system log file found! Exception: %s' % exc)
            self.bot.send_message(
                self.message.chat.id, 'Ошибка при отправке файла')


#
# message handlers
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
        sender = Sender(bot, message, answer)
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
