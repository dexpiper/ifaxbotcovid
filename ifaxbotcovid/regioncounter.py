import re
import random

class RegionCounter():

    def __init__(self, rawtext, table_type=None, short=None):
        self.rawtext = rawtext
        self.table_type = table_type
        self.short = short
        self.log = []
        self.REGEXES = [r'\d+\.\s+(.+)\s+\-?\s+?(\d+)\n', # первая таблица, стандартный
           r'\d+\.\s+(.+)\s+(\d+)\s?\n', # первая таблица, без тире
           r'\d+\.\s+(.+)\s+(\d+)\s?\r', # первая таблица без тире и с другим переносом
           r'(.+)\s–\s?(\d+)\s?', # вторая таблица, с тире
           r'(.+)\s-\s?(\d+)\s?', # вторая таблица, с коротким дефисом
           r'\d+[ , \t]{1,2}([А-я, \-, \-, , \., \(, \)]+)\s+(\d+)', # первая таблица, новый вариант
           r'(.+)\s+(\d+)\s?\n', # вторая таблица, без тире и дефисов
           r'\d+\.\s+(.+)\s+(\d+)\n?\r', # первая таблица с другим переносом
           r'(.+)\s+(\d+)\n?\r' # вторая таблица, без тире и дефисов, с другим переносом
           ]
        
        # константа LIBRARY - словарь дополнений к каждому из типов таблиц
        self.LIBRARY = {

        'new_cases' : {
        'parental_small' : ['новых случая', 'новых диагноза', 'диагноза', 'новых пациента', 'пациента', '-'],
        'dative' : ['новому случаю', 'заболевшему', 'новому диагнозу', 'диагнозу', 'новому заболевшему', '-'],
        'parental_high' : ['новых случаев', 'новых диагнозов', 'новых пациентов', '-']
        },

        'recovered' : {
        'parental_small' : ['выздоровевших', 'выписанных', 'выписанных пациента', '-', '-', '-'],
        'dative' : ['выписанному пациенту', 'выздоровевшему', '-'],
        'parental_high' : ['выздоровевших', 'выписанных', 'выписанных пациентов', '-', '-', '-']
        },

        
        'dead' : {
        'parental_small' : ['летальных исхода', '-'],
        'dative' : ['летальному случаю', 'умершему', '-'],
        'parental_high' : ['летальных случаев', 'умерших', '-']
        },

        'default': {
        'parental_small' : ['-'],
        'dative' : ['-'],
        'parental_high' : ['-']
        }
        
        }

        # константа regionsdict_regs задает словарь изменений в названиях республик РФ, АО и городов фед.значения
        self.regionsdict_regs = {'Адыг' : 'Адыгее',
        'Республика Алтай' : 'Республике Алтай', # первый раз
        'Республика Горный Алтай' : 'Республике Алтай', # второй раз на случай странного названия
        'Алтайск' : 'Алтайском крае', # чтобы не было путаницы с Республикой Алтай
        'Башк' : 'Башкирии',
        'Бурят' : 'Бурятии',
        'Дагест' : 'Дагестане',
        'Ингуш' : 'Ингушетии',
        'Кабардин' : 'Кабардино-Балкарии',
        'Калмык' : 'Калмыкии',
        'Карачаево' : 'Карачаево-Черкессии',
        'Карел' : 'Карелии',
        'Коми' : 'Коми',
        'Крым' : 'Крыму',
        'Марий' : 'Марий Эл',
        'Мордов' : 'Мордовии',
        'Якут' : 'Якутии', # "Саха" зарезервирована под Сахалинскую область
        'Осетия' : 'Северной Осетии',
        'Татарста' : 'Татарстане',
        'Тыва' : 'Тыве',
        'Удмурт' : 'Удмуртии',
        'Хакас' : 'Хакасии',
        'Чеч' : 'Чечне',
        'Чуваш' : 'Чувашии',
        'Москв' : 'Москве',
        'Санкт-Петерб' : 'Санкт-Петербурге',
        'Севастопол' : 'Севастополе',
        'Ханты-Манс' : 'Ханты-Мансийском АО',
        'Ямало-Ненецк' : 'Ямало-Ненецком АО',
        'Еврейск' : 'Еврейской АО',
        'Чукот' : 'Чукотском АО'
        }

    def regsort(self, regs): # сортирует регионы по порядку
        regs_for_sort = ['область', 'край', 'АО', 'Москв', 'Петерб', 'Севастопол']
        for item in regs_for_sort:
            for k in range(len(regs)):
                for i in range(len(regs)):
                    if item in regs[i]:
                        spam = regs[i]
                        del regs[i]
                        regs.append(spam)
                        break
        return regs

    def editRegs(self, rg, mode): # меняет окончания в словах
        if mode == 0:
            FemRegex = re.compile(r'кая')
            rg = FemRegex.sub('кой', rg)
            MaleRegex = re.compile(r'кий')
            rg = MaleRegex.sub('ком', rg)
            oblastRegex = re.compile(r'область')
            rg = oblastRegex.sub('области', rg)
            krayRegex = re.compile(r'край')
            rg = krayRegex.sub('крае', rg)
        if mode == 1:
            for item in self.regionsdict_regs.keys():
                if item in rg:
                    rg = self.regionsdict_regs[item]
        return rg

    def addition(self, key): # добавляет дополнение
        declensional_dict_cases = self.LIBRARY[self.table_type]

        select1 = declensional_dict_cases['parental_small']
        select2 = declensional_dict_cases['dative']
        select3 = declensional_dict_cases['parental_high']
        if int(key) <= 4:
            if int(key) != 1:
                return select1[random.randint(0, len(select1) - 1)]
            else:
                return select2[random.randint(0, len(select2) - 1)]
        else:
            if key[-1] == '1' and key != '11':
                return select2[random.randint(0, len(select2) - 1)]
            elif key[-1] in ['2', '3', '4'] and key not in ['12', '13', '14']:
                return select1[random.randint(0, len(select1) - 1)]
            else:
                return select3[random.randint(0, len(select3) - 1)]

    def process_it(self, dct, key, dot, txt='', regs=''):
        if len(dct[key]) > 1: # если в списке больше одного региона
            dct[key] = self.regsort(dct[key])
            k = 0                          # счетчик регионов
            for reg in dct[key]:
                if k == len(dct[key]) - 1: # узнаем, последний ли регион в списке
                    regs += self.editRegs(reg, 1)
                else:
                    regs += self.editRegs(reg, 1) + ', ' # если не последний, ставим запятую
                k += 1
            regs = self.editRegs(regs, 0)
            if self.table_type != 'default':    # выполняется, если тип таблицы удалось определить
                if dot == True:            # предыдущее закончилось точкой
                    txt += 'По {0} {1} в {2}. '.format(key, self.addition(key), regs)
                else:
                    txt += 'по {0} {1} в {2}. '.format(key, self.addition(key), regs)
                dot = True
            else:                          # выполняется, если тип таблицы определить не удалось
                if dot == True:
                    txt += 'По {0} в {1}. '.format(key, regs)
                else:
                    txt += 'по {0} в {1}. '.format(key, regs)
                dot = True
            
        else:                 # если в списке всего один регион
            regs = dct[key][0]
            regs = self.editRegs(regs, 1); regs = self.editRegs(regs, 0) # преобразуем форму слов
            txt += '{0} - в {1}, '.format(key, regs)
            dot = False
        return txt, dot
    
    def processReg(self, dct): # функция обрабатывает каждый найденный регион и формирует итоговый текст
        txt = ''
        dot = True                # закончилась ли предыдущая фраза точкой
        for key in dct.keys():
            if self.short != None:
                if int(key) >= self.short:
                    n_txt, dot = self.process_it(dct, key, dot)
                    txt += n_txt
                else:
                    return txt
            else:
                n_txt, dot = self.process_it(dct, key, dot)
                txt += n_txt
        if txt[-1] == ',':
            txt[-1] = '.'            
        return txt

    def DetectTable(self): # определяем тип таблицы по ключевым словам
        table_variants_dict = {
            r'по субъектам' : 'new_cases',
            r'ыписан' : 'recovered',
            r'летальн' : 'dead'
            }
        for table_variant in table_variants_dict.keys():
            if table_variant in self.rawtext:
                return table_variants_dict[table_variant]
        return 'default'
        # функция возвращает: 'new_cases', 'recovered', 'dead' или 'default'
        
    def RegexTry(self): # функция пробует составить список регионов разными способами
        counter = 0
        for regex in self.REGEXES:
            counter += 1
            line_regex = re.compile(regex)
            rawregion = line_regex.findall(self.rawtext)
            if rawregion != [] and len(rawregion) > 3:
                self.log.append('Попытка {} из {} - успешно!'.format(counter, len(self.REGEXES)))
                return rawregion
            else:
                self.log.append('Попытка {} из {} неудачна'.format(counter, len(self.REGEXES)))
        return []

    def DeleteSpaces(self, txt): # функция удаляет лишние пробелы
        regex1 = re.compile(r'\s{2,}') # более двух пробелов подряд
        regex2 = re.compile(r'\s{1,},') # перед запятыми
        regex3 = re.compile(r'\s{1,}\.') # перед точками
        txt = regex1.sub('', txt)
        txt = regex2.sub(',', txt)
        txt = regex3.sub('.', txt)
        return txt

    def dictSort(self, dct): # функция сортирует регионы в словаре по количеству
        sort_list = sorted(dct.items(), key=lambda x: int(x[0]), reverse=True)
        newdct = {}
        for item in sort_list:
            newdct[item[0]] = item[1]
        return newdct

    def __call__(self): # главная функция
        if self.table_type == None:
            self.table_type = self.DetectTable() # выясняем тип таблицы
            self.log.append('Тип обработанной таблицы: {}'.format(self.table_type))
        else:
            self.log.append('Тип обработанной таблицы: {}'.format(self.table_type))
        self.rawtext = self.rawtext + '\n' + '\r' # добавляем перенос, чтобы последний регион в списке не выпадал
        rawregion = self.RegexTry() # пробуем составить список регионов

        if rawregion != []:
            self.log.append('Список регионов построен')
        else:
            self.log.append('Список регионов не построен. Ошибка в заданных данных')
            return 'Список регионов не построен. Ошибка в заданных данных'

        counter = 0
        regiondict = {}
        for i in rawregion:                       # далее в цикле создаем словарь из списка с регионами
            if i[1] not in regiondict.keys():
                regiondict[i[1]] = [i[0]]
            else:
                regiondict[i[1]].append(i[0])
            counter += 1

        regiondict = self.dictSort(regiondict)

        # regiondict - {'количество' : ['субъект0', 'субъект1'...]}
        # regiondict.keys() - 'цифра', 'цифра'...
        # regiondict['количество'] - список регионов

        self.log.append('Всего посчитано {} регионов'.format(counter))
        text = self.processReg(regiondict)
        text = self.DeleteSpaces(text)

        return text


# for manual testing only
if __name__ == '__main__':

    import pyperclip
    if pyperclip.paste is not None:
        rawtext = pyperclip.paste()
    else:
        print('No text in clipboard')

    R = RegionCounter(rawtext)
    text = R()
    for el in R.log:
        print(el)
    pyperclip.copy(text)
    print('Готовый тест скопирован в буфер обмена')
