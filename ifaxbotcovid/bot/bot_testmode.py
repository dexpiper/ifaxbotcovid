import logging
from logging.config import fileConfig

from ifaxbotcovid.config.utils import settings
from ifaxbotcovid.bot.factory import create_app, create_bot, create_chef


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

app = create_app()
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

# registering into flask
app.config['TELEBOT'] = bot
app.config['TELEBOT_LOGGER'] = tblogger
app.config['COVIDCHEF'] = chef


with app.app_context():

    from ifaxbotcovid.bot.handlers import BotHandlers
    BotHandlers.register()


def run_long_polling():
    botlogger.info('Starting polling...')
    bot.infinity_polling()
