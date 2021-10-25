import os
import logging

from ifaxbotcovid.bot import factory
from ifaxbotcovid.config import settings


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

    # registering handlers
    from ifaxbotcovid.bot import handlers
