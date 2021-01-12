'''
Constructor of the 'COVID Testing' (Russian: 'ТЕСТИРОВАНИЕ') block of text.
Takes raw message with the amount of performed COVID-19 tests in Russia for the
last 24 hours and returns ready-to-use text.

USAGE:

rpn = RPN(rawtext)
text = rpn()
log = rpn.log

'''

import re, pyperclip
import schemes
import dateline

class RPN:

    def __init__(self, rawtext):
        self.rawtext = rawtext
        self.regexes = {
            'total_tests' : r'РФ проведен\w? более (\d+,?\d?) млн\.? тест\w+ на корона',
            'recent_tests' : r'за сутки проведено (\d+) тыс. тестов на коронав',
            'people_monitored' : r'под меднаблюдением оста\wтся (\d+\s\d+) чел'
            }

        self.values = {
            'total_tests' : 'NO_VALUE',
            'recent_tests' : 'NO_VALUE',
            'people_monitored' : 'NO_VALUE'
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
                return item
        else:
            return value

    def find_values(self): 
        
        '''
        Method fetches values from the given rawtext 
        {'total_tests' : '...', ''recent_tests' : '...', 'people_monitored' : '...'}
        '''

        self.log.append(
            '\n         *** Запускаю поиск переменных для пресс-релиза РПН. Результаты:\n'
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
                    'Переменная не заполнена: {} ({})'.format(value_name, exc)
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
            result = schemes.rpn.format(
                date_day=date_day,
                total_tests=total_tests,
                recent_tests=recent_tests,
                people_monitored=people_monitored
                )
        except Exception as exc:
            self.log.append('<b>Exception при попытке заполнить rpn:</b> ' + str(exc))
            return None
        return result

# for testing usage only
if __name__ == '__main__':
    input('''\n\n         *** Скопируйте в буфер обмена сообщение РПН с количеством выполненных тестов и нажмите "ENTER"''')
    if pyperclip.paste is not None:
        rawtext = pyperclip.paste()
    else:
        print('В буфере обмена отсутствует подходящий кусок текста')
    rpn = RPN(rawtext)
    text, log = rpn.construct(), rpn.log
    print(log)
    print(text)
