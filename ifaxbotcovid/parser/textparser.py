import logging
import re

import ifaxbotcovid.config.schemes as s
import ifaxbotcovid.config.settings as settings
import ifaxbotcovid.parser.dateline as dateline
import ifaxbotcovid.parser.regexp.regex
import ifaxbotcovid.parser.tables as tables
from ifaxbotcovid.parser.utils import ParserHelpers


class Parser():

    def __init__(
            self,
            txt: str,
            mode='Normal',
            short: int = 300,
            logger=logging.getLogger(__name__),
            asfile: bool = False
    ):

        dl = dateline.Dateline()
        self.date_dateline, self.date_day = dl.dateline, dl.weekday

        self.regexes = ifaxbotcovid.parser.regexp.regex.regexes

        self.values = {
          'russia_new_cases': 'NO_VALUE',
          'russia_current_pace': 'NO_VALUE',
          'russia_new_deaths': 'NO_VALUE',
          'russia_new_recovered': 'NO_VALUE',
          'russia_total_cases': 'NO_VALUE',
          'moscow_new_cases': 'NO_VALUE',
          'moscow_new_deaths': 'NO_VALUE',
          'moscow_new_recovered': 'NO_VALUE',
          'date_dateline': self.date_dateline,
          'date_day': self.date_day,
          'golden_cite': 'NO_VALUE',
          'russia_total_deaths': 'NO_VALUE',
          'russia_total_recovered': 'NO_VALUE',
          'russia_active': 'NO_VALUE',
          }
        self.log = []
        self.txt = txt
        self.mode = mode
        self.short = ParserHelpers.check_short(short)
        if self.mode == 'Normal':
            self.flash_pattern = s.flash
            self.text_pattern = s.text
        self.logger = logger
        self.asfile = asfile

    def NAcounter(self):
        i = 0
        for value in self.values.values():
            if value == 'NO_VALUE':
                i += 1
        return i

    def del_space(self, txt):
        '''
        Функция удаляет лишние пробелы
        '''
        regex1 = re.compile(r'\s')
        txt = regex1.sub('', txt)
        return txt

    def get_key(self, dct, v):
        '''
        Функция возвращает key в dict, зная value
        '''
        return [key for key, value in dct.items() if value == v][0]

    def compute_russia_active(self):
        cases = self.values['russia_total_cases']
        deaths = self.values['russia_total_deaths']
        recovered = self.values['russia_total_recovered']
        if (
            cases != 'NO_VALUE' and
            deaths != 'NO_VALUE' and
            recovered != 'NO_VALUE'
        ):

            active = int(cases) - (int(deaths) + int(recovered))
            self.values['russia_active'] = str(active)
        else:
            self.log.append(
                ''.join((
                    'Одна из трех переменных',
                    ' (',
                    'russia_total_cases,',
                    'russia_total_deaths,',
                    'russia_total_recovered',
                    ') ',
                    'не заполнена, поэтому не удается рассчитать russia_active'
                ))
            )

    def find_values(self):
        self.log.append(
            ' '.join((
                ' '*8,  # eight spaces
                '*** <b>Запускаю поиск переменных.',
                'Результаты:</b>\n'

            ))
        )
        for regex in self.regexes.values():
            value_name = self.get_key(self.regexes, regex)
            try:
                value_regex = re.compile(regex, re.DOTALL)
                raw_value = value_regex.findall(self.txt)[0]
                self.log.append(f'<b>{value_name}</b> : {raw_value}')
                raw_value = ParserHelpers.choose_value(raw_value)
                if value_name != 'golden_cite':
                    self.values[value_name] = self.del_space(raw_value)
                else:
                    self.values[value_name] = raw_value
            except Exception:
                self.log.append(
                    f'<b>Переменная не заполнена: {value_name}</b>'
                )
        self.compute_russia_active()

    @staticmethod
    def fool_check(values_dct):
        message = []
        reference = settings.base_vars
        for element in reference.items():
            var = element[0]
            reference_value = element[1]
            try:
                if int(values_dct[var]) >= int(reference_value):
                    pass
                else:
                    message.append(
                        ' '.join((
                            f'Значение переменной {var} ({values_dct[var]})',
                            f'меньше референсного значения {reference_value}'
                        ))
                    )
            except Exception:
                pass
        if len(message) >= 1:
            message.insert(0, '***   ВНИМАНИЕ!')
            message.append(
                '\n\n!!! Рекомендуется проверить отправленный боту текст.\n'
            )
            return '\n'.join(message)
        else:
            return False

    def fill_the_gaps(self):

        try:
            # .format_map(VALUES) не используется,
            # т.к. некоторые данные в словаре нужно предобработать
            flash = self.flash_pattern.format(
                        russia_new_cases=ParserHelpers.change_shape(
                            self.values['russia_new_cases'], caps=True
                        ),
                        russia_current_pace=self.values['russia_current_pace'],
                        russia_new_deaths=self.values['russia_new_deaths'],
                        russia_new_recovered=ParserHelpers.change_shape(
                            self.values['russia_new_recovered'], caps=True
                        ),  # меняем точку на запятую, делим на 1000, округляем
                        russia_total_cases=self.values['russia_total_cases'],
                        moscow_new_cases=ParserHelpers.change_shape(
                            self.values['moscow_new_cases'], caps=True
                        ),
                        moscow_new_deaths=self.values['moscow_new_deaths'],
                        moscow_new_recovered=ParserHelpers.change_shape(
                            self.values['moscow_new_recovered'], caps=True
                        ),
                        date_dateline=self.values['date_dateline'],
                        date_day=self.values['date_day']
                    )
        except Exception as exc:
            self.log.append(
                '<b>Exception при попытке заполнить flash:</b> ' + str(exc)
            )

        # пробуем рассчитать таблицы по регионам
        try:
            ready_cases, ready_deaths, tlog = tables.tables(
                self.txt, short=self.short
            )
            self.log.append(
                ' '.join((
                    '\n',
                    ' '*7,  # seven spaces
                    '*** <b>Запускаю анализ таблиц. Результаты:</b>\n'
                ))
            )
            self.log.append(tlog)
        except Exception as exc:
            self.log.append(exc)

        try:
            maintext = self.text_pattern.format(
                russia_new_cases=ParserHelpers.comma1000(
                    self.values['russia_new_cases']
                ),  # меняем точку на запятую, делим на 1000, округляем
                russia_current_pace=self.values['russia_current_pace'],
                russia_new_deaths=self.values['russia_new_deaths'],
                russia_new_recovered=ParserHelpers.change_shape(
                    self.values['russia_new_recovered']
                ),  # 1098007 ==> 1 млн 98 тыс. 007
                russia_total_cases=ParserHelpers.change_shape(
                    self.values['russia_total_cases']
                ),
                russia_total_deaths=ParserHelpers.change_shape(
                    self.values['russia_total_deaths']
                ),
                russia_total_recovered=ParserHelpers.change_shape(
                    self.values['russia_total_recovered']
                ),
                russia_active=ParserHelpers.change_shape(
                    self.values['russia_active']
                ),
                moscow_new_cases=ParserHelpers.change_shape(
                    self.values['moscow_new_cases']
                ),
                moscow_new_deaths=self.values['moscow_new_deaths'],
                moscow_new_recovered=ParserHelpers.change_shape(
                    self.values['moscow_new_recovered']
                ),
                date_dateline=self.values['date_dateline'],
                date_day=self.values['date_day'],
                golden_cite=self.values['golden_cite'],
                ready_cases=ready_cases,
                ready_deaths=ready_deaths
            )
        except Exception as exc:
            maintext = '<b>Произошла ошибка, текст построить не удалось</b>'
            self.log.append(
                '<b>Ошибка при попытке заполнить maintext:</b> ' + str(exc)
            )

        result = flash + maintext

        return result

    def __call__(self):
        self.logger.debug('Parser called')
        attention_message = ''
        self.find_values()
        result = self.fill_the_gaps()
        if (len(result) >= 4090) and not self.asfile:
            self.logger.debug(
                'Resulting message too long. Trying to shorten')
            # увеличение self.short укорачивает
            # таблицу новых случаев COVID-19 в регионах
            for i in range(6):
                self.log = []
                self.short += 50
                self.find_values()
                result = self.fill_the_gaps()
                # лимит Telegram на длину одного сообщения
                if len(result) <= 4090:
                    break
        check_message = self.fool_check(self.values)
        if check_message:
            attention_message += check_message
        if 'NO_VALUE' in result:
            attention_message += ' '.join((
                '***   ВНИМАНИЕ!',
                str(self.NAcounter()),
                'цифры(-у) или значения(-ний) в тексте релиза',
                'найти не удалось',
                '(заменено на "NO_VALUE").\n\n'
            ))
        if len(attention_message) > 1:
            self.logger.debug('Return resulting text with a warning')
            return (attention_message, result)
        else:
            self.logger.debug('Return resulting text, no warning')
            return ('', result)
