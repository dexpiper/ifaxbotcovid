import logging

from ifaxbotcovid.bot import factory
from ifaxbotcovid.config.utils import settings


def test_telebot_creation():
    test_token = 'This098is0987token'
    bot = factory.create_bot(test_token)
    assert bot
    assert bot.token == test_token


def test_chef_creation():
    botlogger = logging.getLogger('botlogger')
    chef = factory.create_chef(
            short_procedure_key=settings.short_procedure_key,
            check_phrases=settings.key_words,
            stop_phrase=settings.stop_phrase,
            maxlen=3,
            time_gap=1.5,
            logger=botlogger
        )
    assert chef.logger == botlogger
    assert chef.short_procedure_key == settings.short_procedure_key
    assert chef.storage.maxlen == 3
    assert chef.storage.time_gap == 1.5
    assert chef.storage.check_phrases == settings.key_words
    assert chef.storage.stop_phrase == settings.stop_phrase


def test_app_creation():
    app = factory.create_app()
    assert app
