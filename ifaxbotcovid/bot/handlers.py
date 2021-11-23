import functools
import logging

from flask import current_app

from ifaxbotcovid.config.utils import settings, startmessage, helpmessage
from ifaxbotcovid.bot.utils import Sender, CommandParser


app = current_app
with app.app_context():
    bot = app.config['TELEBOT']
    botlogger = app.config['TELEBOT_LOGGER']
    chef = app.config['COVIDCHEF']


class BotHandlers:
    '''
    Message handlers.
    For use only within app.app_context.

    Every single handler function should be decorated
    with custom @handler decorator.
    '''

    handlers = []

    @classmethod
    def register(cls):
        '''
        Register message handlers defined below into a TeleBot.
        '''
        try:
            for handler in BotHandlers.handlers:
                name = handler[0]
                kwargs = handler[1]
                bot.register_message_handler(name, **kwargs)
            return True
        except Exception as exc:
            logging.error('Cannot register handlers: %s', exc)
            return False

    def handler(append_to=handlers, **out_kwargs):
        '''
        Decorator to register telebot handlers
        '''

        def decorator_register(func):
            if out_kwargs:
                append_to.append((func, out_kwargs))

            @functools.wraps(func)
            def wrapper_register(*args, **kwargs):

                return func(*args, **kwargs)

            return wrapper_register
        return decorator_register

    @handler(append_to=handlers, commands=['start'])
    def answer_start(message):
        '''
        Bot sends welcome message
        '''
        bot.send_message(
            message.chat.id,
            startmessage.startmsg(),
            parse_mode='HTML'
        )
        botlogger.info(
            'User %s issued "start" command' % message.from_user.username)
        user = message.from_user.username
        chat_id = message.chat.id
        if (user, chat_id) not in settings.users:
            settings.users.append((user, chat_id))

    @handler(append_to=handlers, commands=['help'])
    def answer_help(message):
        '''
        Bot sends help message
        '''
        botlogger.info(
            'User %s issued "help" command' % message.from_user.username)
        bot.send_message(
            message.chat.id,
            helpmessage.helpmsg(),
            parse_mode='HTML'
        )

    @handler(append_to=handlers, commands=['log'])
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
                botlogger.error(
                    'No system log file found! Exception: %s' % exc)
        else:
            botlogger.warning('Access to user %s denied' % user)
            bot.send_message(
                message.chat.id, '<b>Access denied</b>', parse_mode='HTML'
            )

    @handler(append_to=handlers, content_types=['text'])
    def user_request(message):
        botlogger.info(
            'User %s send some text' % message.from_user.username)
        commands = CommandParser.get_settings(message)
        if commands.short:
            botlogger.info(
                'User %s requested a boundary cut' % message.from_user.username
            )
            answer = chef.process_new_message(
                message=message,
                asfile=commands.asfile,
                short=commands.short
            )
        else:
            answer = chef.process_new_message(
                message=message, asfile=commands.asfile
            )
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
