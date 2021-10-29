import logging
import time
from typing import NamedTuple

from ifaxbotcovid.bot.helpers import LogConstructor, MessageStorage
from ifaxbotcovid.parser.rpn import RPN
from ifaxbotcovid.parser.textparser import Parser


class CovidChef():
    '''
    Provides main logic to concatenate user messages
    sent one by one, call parsers on them - <rpn> or
    <textparser> depending on the message contents, -
    and return processed text, warning message and log.

    Usage:
        covid_chef = CovidChef(short_procedure_key,
            **MessageStorage_kwargs)
        answer = covid_chef.process_new_message(message)
        if answer.flag:
            <send to answer.message_object.chat.id
            answer.warning_message, answer.ready_text
            and answer.log>

    Return namedtuple <Answer> with:
        - warnmessage(str):
                text that warns user that parser could not find
                some variable in given text. Could be empty ('')
        - ready_text(str):
                ready news material cooked by the appropriate
                parser. Empty only if <flag> attribute is False
        - log(str):
                a one-string log issued by the parser.
        - message_object(telebot.types.Message):
                stores key data about message - user and chat.id.
        - flag(bool, default: True):
                True if CovidBot did its work well and made an
                answer that should be sent back to the user.
                False if there is no answer and no reaction needed.
    '''
    class Answer(NamedTuple):
        warnmessage: str
        ready_text: str
        log: str
        message_object: object
        flag: bool = True

    def __init__(self,
                 # a keyword to decide which method to call
                 short_procedure_key: str = '',
                 # and MassageStorage args:
                 maxlen: int = 3,
                 check_phrases: list = [],
                 stop_phrase: str = '',
                 time_gap: float = 1.5,
                 # optional logger instance
                 logger=logging.getLogger(__name__)
                 ):

        storage_kwargs = dict(
            maxlen=maxlen,
            check_phrases=check_phrases,
            stop_phrase=stop_phrase,
            time_gap=time_gap
        )
        self.storage = MessageStorage(**storage_kwargs)
        self.short_procedure_key = short_procedure_key
        self.logger = logger

    def process_new_message(self,
                            message: object,
                            time=int(time.time())) -> Answer:
        '''
        Take message, store it in MessageStorage, check if
        it should be concatenated with previous messages and
        pass it to appropriate inner handler: short_answer or
        long_answer.
        If message should be skipped, message is passed to
        empty_answer handler.
        '''
        self.logger.debug('New message came')
        if self.short_procedure_key in message.text:
            self.logger.debug('Message recognized as RPN report')
            return self.cook_short_answer(message)
        else:
            self.storage.append(
                text=message.text,
                chat_id=message.chat.id,
                time=time)
            # append previous messages
            joint_message = self.storage.get_joint()
            if joint_message.valid:
                self.logger.debug('Message marked as valid')
                self.storage.drop()
                return self.cook_long_answer(joint_message, message)
            else:
                self.logger.debug('Message skipped')
                return self.cook_empty_answer(message)

    def cook_short_answer(self,
                          message: object) -> Answer:
        raw_text = message.text
        RPN_constructor = RPN(raw_text)
        ready_text = RPN_constructor.construct()
        log = LogConstructor.join_log_message(RPN_constructor.log)
        self.logger.debug('Short answer cooked')
        return CovidChef.Answer(
            warnmessage='', ready_text=ready_text, log=log,
            message_object=message
        )

    def cook_long_answer(self,
                         joint_message,
                         message: object) -> Answer:
        '''
        Call ifaxbotcovid.parser.textparser to process
        long COVID-19 press-release: take data out of it
        and place into template to make a ready news text.
        '''
        raw_text = joint_message.text
        news_parser = Parser(raw_text, logger=self.logger)
        warn_message, ready_text = news_parser()
        log = LogConstructor.join_log_message(news_parser.log)
        self.logger.debug('Long answer cooked')
        return CovidChef.Answer(
            warn_message, ready_text, log, message)

    def cook_empty_answer(self,
                          message: object) -> Answer:
        '''
        An empty answer. <Flag> parameter set to False.
        '''
        self.logger.debug('Empty answer returned')
        return CovidChef.Answer('', '', '',
                                message_object=message,
                                flag=False)
