import re

import ifaxbotcovid.dateline as dateline
import ifaxbotcovid.regioncounter as regioncounter
import ifaxbotcovid.config.schemes as s
import ifaxbotcovid.tables as tables
import ifaxbotcovid.config.regex as regex

class Parser():

    def __init__(self, txt, mode='Normal', short=100):

        dl = dateline.Dateline()
        self.date_dateline, self.date_day = dl.dateline, dl.weekday

        self.regexes = regex.regexes
        
        self.values = {'russia_new_cases' : 'NO_VALUE',
          'russia_current_pace' : 'NO_VALUE',
          'russia_new_deaths' : 'NO_VALUE',
          'russia_new_recovered' : 'NO_VALUE',
          'russia_total_cases' : 'NO_VALUE',
          'moscow_new_cases' : 'NO_VALUE',
          'moscow_new_deaths' : 'NO_VALUE',
          'moscow_new_recovered' : 'NO_VALUE',
          'date_dateline' : self.date_dateline,
          'date_day' : self.date_day,
          'golden_cite' : 'NO_VALUE',
          'russia_total_deaths' : 'NO_VALUE',
          'russia_total_recovered' : 'NO_VALUE',
          'russia_active' : 'NO_VALUE',
          }
        self.log = []
        self.txt = txt
        self.mode = mode
        self.short = short
        if self.mode == 'Normal':
            self.flash_pattern = s.flash
            self.text_pattern = s.text
    
    def NAcounter(self):
        i = 0
        for value in self.values.values():
            if value == 'NO_VALUE':
                i += 1
        return i

    def del_space(self, txt): # функция удаляет лишние пробелы
        regex1 = re.compile(r'\s')
        txt = regex1.sub('', txt)
        return txt

    def get_key(self, dct, v): # функция возвращает key в dict, зная value
        return [key for key, value in dct.items() if value == v][0]

    def choose_value(self, value): # функция сокращает tuple вида ('', 'цифра', '') до 'цифра'
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

    def compute_russia_active(self):
        cases = self.values['russia_total_cases']
        deaths = self.values['russia_total_deaths']
        recovered = self.values['russia_total_recovered']
        if cases != 'NO_VALUE' and deaths != 'NO_VALUE' and recovered != 'NO_VALUE':
            active = int(cases) - (int(deaths) + int(recovered))
            self.values['russia_active'] = str(active)
        else:
            self.log.append('Одна из трех переменных (russia_total_cases, russia_total_deaths, russia_total_recovered)  не заполнена, поэтому не удается рассчитать russia_active')
        

    def find_values(self):
        self.log.append('         *** <b>Запускаю поиск переменных. Результаты:</b>\n')
        for regex in self.regexes.values():
            value_name = self.get_key(self.regexes, regex)
            try:
                value_regex = re.compile(regex, re.DOTALL)
                raw_value = value_regex.findall(self.txt)[0]
                self.log.append('<b>{}</b> : {}'.format(value_name, raw_value))
                raw_value = self.choose_value(raw_value)
                if value_name != 'golden_cite':
                    self.values[value_name] = self.del_space(raw_value)
                else:
                    self.values[value_name] = raw_value
            except Exception:
                self.log.append('<b>Переменная не заполнена: {}</b>'.format(value_name))
        self.compute_russia_active()
        
    def comma1000(self, n): # делит на 1000, меняет точку на запятую, округляет (1234 => 1,23)
        try:
            n = round(int(n) / 1000, 2)
            regex1 = re.compile(r'\.')
            n = regex1.sub(',', str(n))
        except Exception as exc:
            print(exc)
        return n

    def comma(self, n): # меняет точку на запятую (1.234 => 1,234)
        regex1 = re.compile(r'\.')
        n = regex1.sub(',', str(n))
        return n

    def change_shape(self, arg): # меняем '1098007' на строку '1 млн 098 тыс. 007' 
        try:
            arg = int(arg) # подстраховываемся на случай, если на входе будет NO_VALUE
            zfill = lambda x: str(x).zfill(3) # объявим безымянную функцию для '7' ==> '007'
        except Exception:
            self.log.append('Не удалось применить change_shape к %s' % str(arg))
            return str(arg)
        if arg > 1000000:
            millions = int(arg/1000000)
            thousands = int(arg/1000) - millions*1000
            hundreds = int(arg) - millions*1000000 - thousands*1000
            return '%s млн %s тыс. %s' % (str(millions), zfill(str(thousands)), zfill(str(hundreds)))
        elif arg > 1000:
            thousands = int(arg/1000)
            hundreds = int(arg) - thousands*1000
            return '%s тыс. %s' % (str(thousands), zfill(str(hundreds)))
        else:
            return str(arg)

    def fill_the_gaps(self):
        
        try:
            flash = self.flash_pattern.format( # .format_map(VALUES) не используется, т.к. некоторые данные в словаре нужно предобработать 
                        russia_new_cases=self.values['russia_new_cases'],
                        russia_current_pace=self.values['russia_current_pace'],
                        russia_new_deaths=self.values['russia_new_deaths'],
                        russia_new_recovered=self.comma1000(self.values['russia_new_recovered']), # меняем точку на запятую, делим на 1000, округляем
                        russia_total_cases=self.values['russia_total_cases'],
                        moscow_new_cases=self.values['moscow_new_cases'],
                        moscow_new_deaths=self.values['moscow_new_deaths'],
                        moscow_new_recovered=self.values['moscow_new_recovered'],
                        date_dateline=self.values['date_dateline'],
                        date_day=self.values['date_day']
                        )
        except Exception as exc:
            self.log.append('<b>Exception при попытке заполнить flash:</b> ' + str(exc))

        # пробуем рассчитать таблицы по регионам
        try:
            ready_cases, ready_deaths, tlog = tables.tables(self.txt, short=self.short)
            self.log.append('\n         *** <b>Запускаю анализ таблиц. Результаты:</b>\n')
            self.log.append(tlog)
        except Exception as exc:
            self.log.append(exc)
            
        try:
            maintext = self.text_pattern.format(
                        russia_new_cases=self.comma1000(self.values['russia_new_cases']), # меняем точку на запятую, делим на 1000, округляем
                        russia_current_pace=self.values['russia_current_pace'],
                        russia_new_deaths=self.values['russia_new_deaths'],
                        russia_new_recovered=self.change_shape(self.values['russia_new_recovered']), # 1098007 ==> 1 млн 98 тыс. 007
                        russia_total_cases=self.change_shape(self.values['russia_total_cases']),
                        russia_total_deaths=self.change_shape(self.values['russia_total_deaths']),
                        russia_total_recovered=self.change_shape(self.values['russia_total_recovered']),
                        russia_active=self.change_shape(self.values['russia_active']),
                        moscow_new_cases=self.change_shape(self.values['moscow_new_cases']),
                        moscow_new_deaths=self.values['moscow_new_deaths'],
                        moscow_new_recovered=self.change_shape(self.values['moscow_new_recovered']),
                        date_dateline=self.values['date_dateline'],
                        date_day=self.values['date_day'],
                        golden_cite=self.values['golden_cite'],
                        ready_cases=ready_cases,
                        ready_deaths=ready_deaths
                        )
        except Exception as exc:
            maintext = '<b>Произошла ошибка, текст построить не удалось</b>'
            self.log.append('<b>Ошибка при попытке заполнить maintext:</b> ' + str(exc))

        result = flash + maintext

        return result

    def __call__(self):
        self.find_values()
        result = self.fill_the_gaps()
        if len(result) >= 4095:
            for i in range(4): # увеличение self.short укорачивает таблицу новых случаев COVID-19 в регионах 
                self.log = []
                self.short += 50
                self.find_values()
                result = self.fill_the_gaps()
                if len(result) <= 4090: # лимит Telegram на длину одного сообщения
                    break
        if 'NO_VALUE' in result:
            attention_message = '***   ВНИМАНИЕ! %s цифры(-у) или значения(-ний) в тексте релиза найти не удалось (заменено на "NO_VALUE").\n\n' % str(self.NAcounter())
            return (attention_message, result)
        return result