import re, pyperclip
import dateline
import regioncounter
import dateline as dl
import schemes as s
import tables

class Parser():

    def __init__(self, txt, mode='Normal', short=100):

        self.date_dateline, self.date_day = dl.TimeRus()

        self.regexes = {'russia_new_cases' : r'случа\w+ коронавирусной инфекции COVID\W19\s?–\s(\d+\s?\d+) в \d+ рег|случа\w+ новой коронавирусной инфекции COVID\W19\s?–\s(\d+\s?\d+) в \d+ рег|случа\w+ новой коронавирусной инфекции \(COVID\W19\)\s?–\s(\d+\s?\d+) в \d+ рег',
           'russia_current_pace' : r'\((\+.+%)\) коронавирусной инфекции в \d+',
           'russia_new_deaths' : r'За последние сутки умер\w+ (\d+) челове|Умерл\w за последние сутки (\d+) челове|За последние сутки подтвержден\w? {1,3}(\d+) {1,3}летальн\w+ случа',
           'russia_new_recovered' : r'За последние сутки выписан\w? (\d+\s\d+)\s+челов|За прошедшие сутки выписан\w? по выздоровлени\w\s{1,3}(\d+\s?\d+) {1,3}человек',
           'russia_total_cases' : r'Российской Федерации нарастающим итогом зарегистрирован\w* (\d+\s?\d+\s?\d+)\s?случа|России нарастающим итогом зарегистрирован\w* (\d+\s?\d+\s?\d+)\s?случа|В Российской Федерации нарастающим итогом зарегистрирован\w? (\d+\s?\d+\s?\d+)\s?случа',
           'moscow_new_cases' : r'Распределение по субъектам.*Москва\s\W?\s?(\d+).*В Российской Федерации нарастающ|Распределение по субъектам.*Москва\s\W?\s?(\d+).*В России нарастающ',
           'moscow_new_deaths' : r'За последние сутки умер\w* \d+ человек.*Москва\s+\W?\s?(\d+).*Умер\w* за весь период|Умер\w* за последние сутки \d+ человек.*Москва\s+\W?\s?(\d+).*За весь период умерл|Умер\w* за последние сутки \d+ человек.*Москва\s+\W?\s?(\d+).*Умер\w* за весь период|За последние сутки умер\w* \d+ человек.*Москва\s+\W?\s?(\d+).*За весь период умерл|За последние сутки подтвержден\w+ {1,3}\d+ {1,3}летальн\w+ случа.*Москва\s+\W?\s?(\d+).*За весь период по России умер',
           'moscow_new_recovered' : r'За последние сутки выписан\w*.*человек\w?.*Москва\s+\W?\s?(\d{3,6}).*За весь период выписан|За последние сутки выписан\w*.*человек\w?.*Москва\s+\W?\s?(\d{3,6}).*Выписан\w* за весь|За прошедшие сутки выписан\w? по выздоровлени\w\s{1,3}\d+\s?\d+ {1,3}человек.*Москва\s+\W?\s?(\d{3,6}).*За весь период выписан',
           'golden_cite' : r'(За последние сутки в.*без клинических проявлений)',
           'russia_total_deaths' : r'За весь период умер\w+\s+(\d+\s?\d+)\s+челов|Умер\w* за весь период (\d+\s?\d+) челов|За весь период по России умер\w+ (\d+\s?\d+) человек|За весь период по России умер\w? (\d+\s?\d+) чел|За весь период по России умерл\w {1,3}(\d+\s?\d+) {1,3}человек',
           'russia_total_recovered' : r'За весь период выписан\w+\s+(\d+\s?\d+\s?\d+)|За весь период выписано по выздоровлению по России\s+–?\s{0,3}(\d+\s?\d+\s?\d+)'
          }
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
            self.text_pattern = s.text2
    
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
                return item
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
            except Exception as exc:
                self.log.append('<b>Переменная не заполнена: {}</b>'.format(value_name))
        self.compute_russia_active()
        #VALUES = manual_edit(VALUES) # если есть незаполненные переменные, предлагаем пользователю ввести их вручную

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
        except Exception as exc:
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
        
if __name__ == '__main__':
    import pprint
    if pyperclip.paste is not None:
        rawtext = pyperclip.paste()
        parser = Parser(rawtext)
        text = parser()
        pyperclip.copy(text)
        pprint.pprint(parser.log)
        
