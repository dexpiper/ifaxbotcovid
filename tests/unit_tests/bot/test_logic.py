import time
from unittest.mock import Mock
from copy import deepcopy

import pytest

from ifaxbotcovid.bot.logic import CovidChef


@pytest.fixture(scope='function')
def args_dict():
    short = 'RPN'
    check = ['Hello', 'Foobar']
    stop = 'Bye'
    time_gap = 1.5
    return dict(
        short_procedure_key=short,
        check_phrases=check,
        stop_phrase=stop,
        time_gap=time_gap
    )


@pytest.fixture(scope='function')
def chef(args_dict):
    return CovidChef(**args_dict)


@pytest.fixture(scope='function')
def msg():
    message_obj = Mock()
    chat_obj = Mock()
    user_obj = Mock()

    chat_obj.id = '98765432112'
    chat_obj.type = 'private'

    user_obj.id = 1234567
    user_obj.is_bot = False
    user_obj.first_name = 'James'
    user_obj.last_name = 'Bond'

    message_obj.message_id = '1234545'
    message_obj.from_user = user_obj
    message_obj.date = int(time.time())
    message_obj.chat = chat_obj
    message_obj.content_type = 'text'
    message_obj.options = {}
    message_obj.json_string = ''

    message_obj.text = ''

    return message_obj


@pytest.fixture(scope='function')
def texts():
    first_text = ' '.join([
        'First part. Hello, Foobar check_phrases are present.',
        'But no stop phrase. So message should be skipped'
    ])
    second_text = 'Some intermediate text. Not yet the end'
    third_text = 'Last part with Bye stop phrase. End!'
    return first_text, second_text, third_text


@pytest.fixture(scope='function')
def messages(texts, msg):

    first_text, second_text, third_text = texts

    msg1 = deepcopy(msg)
    msg2 = deepcopy(msg)
    msg3 = deepcopy(msg)

    msg1.text = first_text
    msg2.text = second_text
    msg2.date += 1          # this message should be +1 sec older than 1st
    msg2.message_id = str(int(msg2.message_id) + 1)
    msg3.text = third_text
    msg3.date += 2          # +1 sec older than second
    msg3.message_id += str(int(msg2.message_id) + 2)

    return msg1, msg2, msg3


class TestCovidChef:

    def test_Chef_creation(self, args_dict):
        chef = CovidChef(**args_dict)
        assert chef.storage

    def test_storage_params_inside_Chef(self, chef, args_dict):
        assert chef.short_procedure_key == args_dict[
            'short_procedure_key'
        ]
        assert chef.storage.check_phrases == args_dict['check_phrases']
        assert chef.storage.stop_phrase == args_dict['stop_phrase']

    def test_storage_funcs_inside_Chef(self, chef):
        last_message = chef.storage._last()
        assert last_message.text == ''
        assert last_message.chat_id == ''
        chef.storage.append(text='HelloWorld', chat_id='123')
        assert chef.storage._last().text == 'HelloWorld'
        assert chef.storage._last().chat_id == '123'

    def test_answer_creation(self, msg):

        init_dct = dict(
            warnmessage='This is a warn message',
            ready_text='This is a long text returned by inner funcs',
            log='This is a log message with <b>tags</b>',
            message_object=msg
        )
        answer = CovidChef.Answer(**init_dct)
        answer_as_dict = answer._asdict()
        for key in init_dct.keys():
            assert answer_as_dict[key] == init_dct[key]

    def test_short_message_with_keyword_processed(self, chef, msg):
        text = '''
        This is a short message with short procedure keyword:
        RPN. Because this keyword exists, CovidChef should call
        its cook_short_answer method.
        '''
        msg.text = text
        answer = chef.process_new_message(msg)
        assert answer.flag is True
        assert 'ТЕСТИРОВАНИЕ' in answer.ready_text

    def test_messages_appended_one_by_one(self, chef, texts, messages):

        msg1, msg2, msg3 = messages
        first_text, second_text, third_text = texts

        # getting answers
        answer1 = chef.process_new_message(msg1)
        assert answer1.flag is False
        assert answer1.message_object == msg1
        assert chef.storage._last().text == first_text
        assert chef.storage._last_before_last().text == ''

        answer2 = chef.process_new_message(msg2)
        assert answer2.flag is False
        assert answer2.message_object == msg2
        assert chef.storage._last().text == second_text
        assert chef.storage._last_before_last().text == first_text

        answer3 = chef.process_new_message(msg3)
        assert msg3.text == third_text
        assert chef.storage._last().text == ''
        assert len(chef.storage) == 1

        assert answer3.flag is True
        assert answer3.warnmessage
        assert answer3.log
        assert answer3.message_object == msg3
        assert answer3.ready_text

        check_ready_text = ['COVID-19', 'МОЛНИЯ', 'случаев']
        for item in check_ready_text:
            assert item.lower() in answer3.ready_text.lower()

    def test_wrong_order(self, chef, messages):

        msg1, msg2, msg3 = messages

        answer1 = chef.process_new_message(msg3)
        assert answer1.flag is False

        answer2 = chef.process_new_message(msg2)
        assert answer2.flag is False

        answer3 = chef.process_new_message(msg1)
        assert answer3.flag is False

    def test_one_good_message(self, chef, texts, msg):
        long_text = ''.join(texts)
        msg.text = long_text
        answer = chef.process_new_message(msg)

        assert answer.flag is True
        assert answer.warnmessage
        assert answer.log
        assert answer.message_object == msg

        assert answer.ready_text
        check_ready_text = ['COVID-19', 'МОЛНИЯ', 'случаев']
        for item in check_ready_text:
            assert item.lower() in answer.ready_text.lower()

        assert chef.storage._last().text == ''
        assert len(chef.storage) == 1

    def test_time_gap_logic(
            self,
            chef, messages):

        t = int(time.time())
        msg1, msg2, msg3 = messages
        msg1.date = t
        msg2.date = t + 2
        msg3.date = t + 4

        answer1 = chef.process_new_message(msg1)
        assert answer1.flag is False

        answer2 = chef.process_new_message(msg2)
        assert answer2.flag is False

        answer3 = chef.process_new_message(msg3)
        assert answer3.ready_text == ''
        assert answer3.flag is False  # gap is too big to glue messages 2gether
