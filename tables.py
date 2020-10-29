import regioncounter as r
import re

'''
Скрипт находит таблицы новых случев и смертей в пресс-релизе оперштаба
и возвращает обработанные скриптом regioncounter.py абзацы с отсортированными
регионами.

Первая таблица - с новыми случаями - должна быть обрезана (убираем все регионы,
где менее 100 случаев за последние сутки. Вторую таблицу даем полностью.
'''

# задаем regex'ы для парсинга двух таблиц в релизе
REGEXES = dict(newcases=r'Распределение по субъектам(.*)В Российской Федерации нарастающ',
           newdeaths=r'подтвержден\w?\s+\d{1,3}\s+летальн\w+ случа\w+(.*)За весь период по России умер')

# здесь будут храниться таблицы
TABLES = dict(newcases='NO_TABLE', newdeaths='NO_TABLE')

def get_key(dct, v): # функция возвращает key в dict, зная value
	return [key for key, value in dct.items() if value == v][0]

def find_tables(raw_txt):
    global TABLES
    for regex in REGEXES.values():
        try:
            table_name = get_key(REGEXES, regex)
        except Exception as exc:
            print('Не удалось определить формат таблицы')
            return
        try:
            table_regex = re.compile(regex, re.DOTALL)
            raw_table = table_regex.findall(raw_txt)[0]
            TABLES[table_name] = raw_table
        except Exception as exc:
            print('Не удалось найти таблицу {}'.format(table_name))
    return

def get_prepared(ready_table, table_type, short=100):
    if table_type == 'ready_cases':
        splitted_ready_cases = ready_table.split(',')
        if 'Москв' in splitted_ready_cases[0]:
            first_reg = splitted_ready_cases[1]
            splitted_ready_cases[1] = first_reg.replace('-', 'новых случаев COVID-19 зафиксировано', 1)
            joined_ready_cases = ','.join(splitted_ready_cases[1:]) # убираем Москву
        else:
            joined_ready_cases = ','.join(splitted_ready_cases) # Москва не в начале, не трогаем
        cases_final = 'По информации оперативного штаба, еще' + joined_ready_cases + 'В других регионах России суточный прирост не превышает ' + str(short) + '.'
        return cases_final
    if table_type == 'ready_deaths':
        splitted_deaths = ready_table.split(',')
        first_reg = splitted_deaths[0]
        if ' - ' in first_reg:
            splitted_deaths[0] = first_reg.replace('-', 'пациентов скончалось за сутки', 1)
        joint_deaths = ','.join(splitted_deaths)
        cases_final = 'Согласно данным оперштаба о смертности, ' + joint_deaths
        return cases_final

def process_tables(short=100):
    rc_ready_cases = r.RegionCounter(TABLES['newcases'], table_type='new_cases', short=short)
    rc_ready_deaths = r.RegionCounter(TABLES['newdeaths'], table_type='dead')
    ready_cases, log1 = rc_ready_cases(), rc_ready_cases.log
    ready_deaths, log2 = rc_ready_deaths(), rc_ready_deaths.log
    log = log1 + log2
    ready_cases = get_prepared(ready_cases, 'ready_cases', short=short)
    ready_deaths = get_prepared(ready_deaths, 'ready_deaths', short=short)
    return ready_cases, ready_deaths, log

def tables(rawtext, short=100): # для вызова за пределами скрипта
    try:
        find_tables(rawtext)
        ready_cases, ready_deaths, log = process_tables(short=short)
        return ready_cases, ready_deaths, log
    except Exception as exc:
            print('Не удалось обработать и добавить таблицы новых случаев и умерших')

if __name__ == '__main__':
    import pyperclip, pprint
    if pyperclip.paste is not None:
        rawtext = pyperclip.paste()
        ready_cases, ready_deaths, log = tables(rawtext, short=150)
        print(ready_cases)
        print(ready_deaths)
        print(log)
    else:
        print('Нет текста в буфере обмена')
