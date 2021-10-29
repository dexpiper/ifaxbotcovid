'''
Rewriting long lists of regions from big press-release to make it
look like real news material. During this process regions are sorted
according to number of COVID-19 cases and region type. Also official
names of rebublics are changed to their common forms, syntactic objects
are added and grammar forms changed according to Russian language rules.

Russian:
Скрипт переписывает табличные списки регионов из пресс-релиза
текстом, как в новости. При этом регионы сортируются по количеству
выявленных случаев коронавируса и типу, официальные названия республик
меняются на короткие (например, Республика Саха - Якутия => в Якутии),
существительные ставятся в форму нужного падежа. Кроме того, добавляются
синтаксические дополнения, чтобы текст выглядел "живым".
'''

import re
import random

from ifaxbotcovid.parser.regexp import table_regex
from ifaxbotcovid.parser.lib import addition_lib
from ifaxbotcovid.parser.lib import regions


class RegionCounter():

    def __init__(self, rawtext, table_type=None, short=None):
        self.rawtext = rawtext
        self.table_type = table_type
        self.short = short
        self.log = []

        # regular expressions to parse tables
        self.REGEXES = table_regex.table_regex

        # LIBRARY - словарь дополнений к каждому из типов таблиц
        self.LIBRARY = addition_lib.addition_lib

        # regionsdict_regs
        self.regionsdict_regs = regions.regions

    def regsort(self, regs):
        '''
        сортирует регионы по порядку
        '''
        regs_for_sort = [
            'область', 'край', 'АО', 'Москв', 'Петерб', 'Севастопол'
        ]
        for item in regs_for_sort:
            for i in range(len(regs)):
                if item in regs[i]:
                    spam = regs[i]
                    del regs[i]
                    regs.append(spam)
                    break
        return regs

    def editRegs(self, rg, mode):
        '''
        Меняет окончания в словах
        '''
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

    def addition(self, key):
        '''
        Добавляет синтаксическое дополнение в зависимости
        от типа таблицы
        '''
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

        # если в списке больше одного региона
        if len(dct[key]) > 1:
            dct[key] = self.regsort(dct[key])
            k = 0  # счетчик регионов
            for reg in dct[key]:
                # узнаем, последний ли регион в списке
                if k == len(dct[key]) - 1:
                    regs += self.editRegs(reg, 1)
                else:
                    # если не последний, ставим запятую
                    regs += self.editRegs(reg, 1) + ', '
                k += 1
            regs = self.editRegs(regs, 0)

            # если тип таблицы удалось определить
            if self.table_type != 'default':
                if dot is True:  # предыдущее закончилось точкой
                    txt += 'По {0} {1} в {2}. '.format(
                        key, self.addition(key), regs)
                else:
                    txt += 'по {0} {1} в {2}. '.format(
                        key, self.addition(key), regs)
                dot = True

            # если тип таблицы определить не удалось
            else:
                if dot is True:
                    txt += 'По {0} в {1}. '.format(key, regs)
                else:
                    txt += 'по {0} в {1}. '.format(key, regs)
                dot = True

        # если в списке всего один регион
        else:
            regs = dct[key][0]

            # преобразуем форму слов
            regs = self.editRegs(regs, 1)
            regs = self.editRegs(regs, 0)
            txt += '{0} - в {1}, '.format(key, regs)
            dot = False
        return txt, dot

    def processReg(self, dct):
        '''
        Функция обрабатывает каждый найденный регион
        и формирует итоговый текст
        '''
        txt = ''
        dot = True  # закончилась ли предыдущая фраза точкой
        for key in dct.keys():
            if self.short is not None:
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

    def DetectTable(self):
        '''
        Определяем тип таблицы по ключевым словам.

        Возвращает: 'new_cases', 'recovered', 'dead' или 'default'
        '''
        table_variants_dict = {
            r'по субъектам': 'new_cases',
            r'ыписан': 'recovered',
            r'летальн': 'dead'
            }
        for table_variant in table_variants_dict.keys():
            if table_variant in self.rawtext:
                return table_variants_dict[table_variant]
        return 'default'

    def RegexTry(self):
        '''
        Пробует составить список регионов разными способами
        '''
        counter = 0
        for regex in self.REGEXES:
            counter += 1
            line_regex = re.compile(regex)
            rawregion = line_regex.findall(self.rawtext)
            if rawregion != [] and len(rawregion) > 3:
                self.log.append(
                    'Попытка {} из {} - успешно!'.format(
                        counter, len(self.REGEXES)
                    )
                )
                return rawregion
            else:
                self.log.append(
                    'Попытка {} из {} неудачна'.format(
                        counter, len(self.REGEXES)
                    )
                )
        return []

    def DeleteSpaces(self, txt):
        '''
        Удаляет лишние пробелы
        '''
        regex1 = re.compile(r'\s{2,}')    # более двух пробелов подряд
        regex2 = re.compile(r'\s{1,},')   # перед запятыми
        regex3 = re.compile(r'\s{1,}\.')  # перед точками
        txt = regex1.sub('', txt)
        txt = regex2.sub(',', txt)
        txt = regex3.sub('.', txt)
        return txt

    def dictSort(self, dct):
        '''
        Cортирует регионы в словаре по количеству
        '''
        sort_list = sorted(
            dct.items(), key=lambda x: int(x[0]), reverse=True
        )
        newdct = {}
        for item in sort_list:
            newdct[item[0]] = item[1]
        return newdct

    def __call__(self):
        '''
        Вызов класса как функции
        '''
        if self.table_type is None:
            self.table_type = self.DetectTable()  # выясняем тип таблицы
            self.log.append(
                'Тип обработанной таблицы: {}'.format(self.table_type)
            )
        else:
            self.log.append(
                'Тип обработанной таблицы: {}'.format(self.table_type)
            )

        # добавляем перенос, чтобы последний регион в списке не выпадал
        self.rawtext = self.rawtext + '\n' + '\r'
        rawregion = self.RegexTry()  # пробуем составить список регионов

        if rawregion != []:
            self.log.append('Список регионов построен')
        else:
            self.log.append(
                'Список регионов не построен. Ошибка в заданных данных'
            )
            return 'Список регионов не построен. Ошибка в заданных данных'

        counter = 0
        regiondict = {}

        # далее в цикле создаем словарь из списка с регионами
        for i in rawregion:
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
