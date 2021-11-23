'''
Constructor of the 'COVID Testing' (Russian: 'ТЕСТИРОВАНИЕ') block of text.
Takes raw message with the amount of performed COVID-19 tests in Russia for the
last 24 hours and returns ready-to-use text.

USAGE:

rpn = RPN(rawtext)
text = rpn.construct()
log = rpn.log

Russian:
Переписывает короткий кусок текста - сообщение пресс-службы Роспотребнадзора
о ситуации с тестированием в России - в готовый абзац для новости.

'''

import re

import ifaxbotcovid.config.utils.tmploader as tmploader
import ifaxbotcovid.parser.dateline as dateline
from ifaxbotcovid.parser.utils import ParserHelpers
from ifaxbotcovid.parser.regexp import rpn_regex


class RPN:

    def __init__(self, rawtext):
        self.rawtext = rawtext
        self.regexes = rpn_regex.rpn_regex
        self.template = tmploader.getrpntemplate()

        self.values = {
            'total_tests': 'NO_VALUE',
            'recent_tests': 'NO_VALUE',
            'people_monitored': 'NO_VALUE'
            }

        self.log = []

    @staticmethod
    def del_space(txt):
        '''
        Deleting unwanted spaces in given string
        '''
        regex1 = re.compile(r'\s')
        txt = regex1.sub('', txt)
        return txt

    @staticmethod
    def get_key(dct, v):
        '''
        Method returns key of given dict by known value
        '''
        return [key for key, value in dct.items() if value == v][0]

    @staticmethod
    def choose_value(value):
        '''
        Method cuts tuple like ('', 'number', '') to 'number'
        '''
        if type(value) == tuple:
            if len(value) > 1:
                for item in value:
                    if item == '':
                        None
                    else:
                        return item
                return ''
            else:
                return value[0]
        else:
            return value

    def find_values(self):

        '''
        Method fetches values from the given rawtext
        {
            'total_tests': '...',
            'recent_tests': '...',
            'people_monitored': '...'
        }
        '''

        self.log.append(
            ' '.join((
                '\n',
                ' '*7,  # seven spaces
                '*** Запускаю поиск переменных для пресс-релиза РПН',
                'Результаты:\n'
            ))
        )
        for regex in self.regexes.values():
            value_name = self.get_key(self.regexes, regex)
            try:
                value_regex = re.compile(regex, re.DOTALL)
                raw_value = value_regex.findall(self.rawtext)[0]
                self.log.append('{} : {}'.format(value_name, raw_value))
                raw_value = self.choose_value(raw_value)
                self.values[value_name] = self.del_space(raw_value)
            except Exception as exc:
                if str(exc) == 'list index out of range':
                    exc = 'Не удалось найти значение'
                self.log.append(
                    f'Переменная не заполнена: {value_name} ({exc})'
                )

    def construct(self):
        '''
        Main call as a function
        '''
        self.find_values()
        total_tests = self.values['total_tests']
        recent_tests = self.values['recent_tests']
        people_monitored = self.values['people_monitored']
        dl = dateline.Dateline()
        date_day = dl.weekday

        try:
            result = self.template.format(
                date_day=date_day,
                total_tests=total_tests,
                recent_tests=recent_tests,
                people_monitored=ParserHelpers.change_shape(
                    people_monitored
                )
            )
        except Exception as exc:
            self.log.append(
                f'<b>Exception при попытке заполнить rpn:</b> {str(exc)}'
            )
            return None
        return result
