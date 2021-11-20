import logging
from collections import namedtuple

from pytest import fixture

from ifaxbotcovid.bot.factory import create_app, create_bot, create_chef
from ifaxbotcovid.config.utils import settings


class TestHandlers:

    @fixture
    def objects(self) -> tuple:
        TOKEN = 'SomeCustomString123'
        botlogger = logging.getLogger('botlogger')
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
        app.config['TELEBOT'] = bot
        app.config['TELEBOT_LOGGER'] = tblogger
        app.config['COVIDCHEF'] = chef
        Objects = namedtuple('Objects', ['app', 'bot', 'chef'])
        answer = Objects(app, bot, chef)
        return answer

    def test_answer_fixture(self, objects):
        assert objects.app
        assert objects.bot
        assert objects.chef

    def test_register_handlers(self, objects):
        with objects.app.app_context():
            from ifaxbotcovid.bot.handlers import BotHandlers
            assert BotHandlers
            assert BotHandlers.register()
