import functools
import logging

from flask import current_app

from ifaxbotcovid.bot.logic import CovidChef
from ifaxbotcovid.config.utils import settings, startmessage, helpmessage
from ifaxbotcovid.bot.helpers import (FileSaver, DocxReader, Sender,
                                      CommandParser, LogConstructor)
from ifaxbotcovid.parser.textparser import Parser


app = current_app
with app.app_context():
    bot = app.config['TELEBOT']
    botlogger = app.config['TELEBOT_LOGGER']
    chef = app.config['COVIDCHEF']
    store = app.config['REDIS_URL']


class BotHandlers:
    """
    Message handlers.
    For use only within app.app_context.

    Every single handler function should be decorated
    with custom @handler decorator.
    """

    handlers = []

    @classmethod
    def register(cls):
        """
        Register message handlers defined below into a TeleBot.
        """
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
        """
        Decorator to register telebot handlers
        """
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
        """
        Bot sends welcome message
        """
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
        """
        Bot sends help message
        """
        botlogger.info(
            'User %s issued "help" command' % message.from_user.username)
        bot.send_message(
            message.chat.id,
            helpmessage.helpmsg(),
            parse_mode='HTML'
        )

    @handler(append_to=handlers, commands=['log'])
    def syslog_sender(message):
        """
        Bot sends system log as a file (admin only)
        """
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

    @handler(append_to=handlers, commands=['short'])
    def answer_short(message):
        value = message.text[6:].strip()
        if not value:
            try:
                value = store.get(key=message.chat.id, cached=True)
            except LookupError:
                botlogger.error(
                    f'Cannot get value for user {message.chat.id} '
                    f'({message.from_user.username})'
                )
                bot.send_message(
                    message.chat.id,
                    'Значение /short для вас не установлено, '
                    'используется значение по умолчанию (300).'
                )
            except Exception as exc:
                botlogger.error(f'Cannot connect to database: {exc}')
                bot.send_message(
                    message.chat.id,
                    '\u274C Не удалось получить данные. Сообщение об ошибке '
                    'сохранено, мы ей займемся. Сейчас используется значение '
                    'по умолчанию (300)'
                )
            else:
                bot.send_message(
                    message.chat.id,
                    f'Значение /short для вас: {value}. '
                    'Для изменения используйте команду /short <цифра>'
                )
            finally:
                return
        try:
            value = int(value)
            assert 100 < value < 700
        except ValueError:
            botlogger.error(f'Cannot extract int value from {message.text}')
            bot.send_message(
                message.chat.id,
                '\u274C Неверный формат данных. Пожалуйста, используйте '
                'команду так: <i>"/short 300"</i>.',
                parse_mode='HTML'
            )
            return
        except AssertionError:
            botlogger.error('Value not in diap 100 < val < 700')
            bot.send_message(
                message.chat.id,
                '\u274C Значение должно быть в диапазоне от <i>100 до 700</i>',
                parse_mode='HTML'
            )
            return
        try:
            store.set(key=message.chat.id, value=value, cached=True)
        except Exception as exc:
            botlogger.error(f'Cannot set value in database: {exc}')
            bot.send_message(
                message.chat.id,
                '\u274C Не удалось внести изменения. Сообщение об ошибке '
                'сохранено, мы ей займемся.'
            )
        else:
            bot.send_message(
                message.chat.id,
                f'\u2705 Новое значение /short {value} для вас сохранено'
            )

    @handler(append_to=handlers, content_types=['text'])
    def user_request(message):
        """
        Store recieved message's text in MessageStorage and check
        if previous messages with the new one form together a valid
        COVID-19 press-release. Call parser to find vars and fill in
        the template. Send ready news material back.
        """
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
            sender = Sender(bot, answer, logger=botlogger,
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
        else:
            botlogger.info('Answer considered invalid')
            bot.send_message(
                message.chat.id,
                '\U0001F4A4 Сообщения отправлены в обработку. Если ответа нет,'
                ' попробуйте отправить текст еще раз или бросьте релиз файлом.'
            )
            return

    @handler(append_to=handlers, content_types=['document'])
    def user_file_request(message):
        """
        Recieve the whole press-release in .docx file. Check and save
        the file, get text from it, parse text, fill in the gaps in template
        and send ready news-material to the user.
        """
        suffix = message.document.file_name.split('.')[-1]
        if suffix != 'docx':
            botlogger.info(f'Unknown file type: {suffix}')
            bot.send_message(
                message.chat.id,
                f'\u274C Ошибка: неизвестный тип файла {suffix} '
                'Мы принимаем только .docx с пресс-релизом оперштаба.')
            return

        # saving file
        botlogger.info(
            f'Got a valid file {message.document.file_name}'
            f' from user {message.from_user.username}'
        )
        try:
            file_path = bot.get_file(message.document.file_id).file_path
            result = bot.download_file(file_path)
            saved_path = FileSaver.from_file(
                contents=result,
                filename=message.document.file_name,
                username=message.from_user.username
            )
        except Exception as exc:
            botlogger.error(
                f'Cannot download or save file from Telegram: {exc}')
            bot.send_message(
                message.chat.id,
                '\u274C Не удалось получить или сохранить файл с Telegram :(\n'
                'Сообщение об ошибке и детали сохранены.'
            )
            return

        botlogger.info('Successfully saved file in %s' % saved_path)
        bot.send_message(
            message.chat.id,
            f'\u2705 Файл {message.document.file_name} успешно отправлен. \n'
            'Обрабатываем... \U0001F4A4',
            parse_mode='HTML'
        )

        # trying to read file
        try:
            reader = DocxReader(saved_path)
            text = reader.to_text()
        except Exception as exc:
            botlogger.error('Cannot read docx file: %s' % exc)
            bot.send_message(
                message.chat.id,
                '\u274C Не удалось прочитать отправленный файл. '
                'Что-то с ним не так( Данные об ошибке сохранены.'
            )
            FileSaver.del_file(saved_path)
            return

        # parsing text from file
        news_parser = Parser(txt=text, asfile=True, short=300)
        warn_message, ready_text = news_parser()
        log = LogConstructor.join_log_message(news_parser.log)
        # constructing and sending answer
        answer = CovidChef.Answer(
            warnmessage=warn_message, ready_text=ready_text,
            log=log, message_object=message)
        sender = Sender(bot, answer, logger=botlogger)
        sender.send_asfile()
        FileSaver.del_file(saved_path)
