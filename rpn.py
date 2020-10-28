'''
Скрипт добавляет в шаблон блок под названием "Тестирование".
Для этого пользователю предлагается скопировать в буфер обмена сообщение Роспотребнадзора (РПН),
в котором ведомство ежедневно отчитывается о количестве выполненных в стране тестов и числе
граждан, находящихся под присмотром медиков.

'''

import re, pyperclip
import schemes
import dateline as dl 

REGEXES = {'total_tests' : r'РФ проведен\w? более (\d+,?\d?) млн\.? тест\w+ на корона',
          'recent_tests' : r'за сутки проведено (\d+) тыс. тестов на коронав',
          'people_monitored' : r'под меднаблюдением оста\wтся (\d+\s\d+) чел'
    }

VALUES = {'total_tests' : 'NO_VALUE',
          'recent_tests' : 'NO_VALUE',
          'people_monitored' : 'NO_VALUE'
    }

LOG = []


def find_text(): # получаем у пользователя сообщение РПН для обработки
    input('''\n\n         *** Скопируйте в буфер обмена сообщение РПН с количеством выполненных тестов и нажмите "ENTER"''')
    if pyperclip.paste is not None:
        rawtext = pyperclip.paste()
    else:
        print('В буфере обмена отсутствует подходящий кусок текста')
    return rawtext

def del_space(txt): # функция удаляет лишние пробелы
    regex1 = re.compile(r'\s')
    txt = regex1.sub('', txt)
    return txt

def get_key(dct, v): # функция возвращает key в dict, зная value
	return [key for key, value in dct.items() if value == v][0]

def choose_value(value): # функция сокращает tuple вида ('', 'цифра', '') до 'цифра'
    if type(value) == tuple:
        if len(value) > 1:
            for item in value:
                if item == '':
                    None
                else:
                    return item
            return ''
        else:
            return item
    else:
        return value

def find_values(rawtext): # функция возвращает словарь {'total_tests' : '...', ''recent_tests' : '...', 'people_monitored' : '...'}
    global VALUES, LOG
    LOG.append('\n         *** Запускаю поиск переменных скрипта RPN.py. Результаты:\n')
    for regex in REGEXES.values():
        value_name = get_key(REGEXES, regex)
        try:
            value_regex = re.compile(regex, re.DOTALL)
            raw_value = value_regex.findall(rawtext)[0]
            LOG.append('{} : {}'.format(value_name, raw_value))
            raw_value = choose_value(raw_value)
            VALUES[value_name] = del_space(raw_value)
        except Exception as exc:
            LOG.append('Переменная не заполнена: {}'.format(value_name))
    return VALUES['total_tests'], VALUES['recent_tests'], VALUES['people_monitored']

def call(rawtext):
    global LOG
    total_tests, recent_tests, people_monitored = find_values(rawtext)
    date_dateline, date_day = dl.TimeRus()
    log = ''
    try:
        rpn_result = schemes.rpn.format(
            date_day=date_day,
            total_tests=total_tests,
            recent_tests=recent_tests,
            people_monitored=people_monitored
            )
    except Exception as exc:
        LOG.append('<b>Exception при попытке заполнить rpn:</b> ' + str(exc))
        return None, LOG
    return rpn_result, LOG

if __name__ == '__main__':
    rawtext = find_text()
    text, log = call(rawtext)
    if 'Exception' in log:
        print(log)
    else:
        print(text)
