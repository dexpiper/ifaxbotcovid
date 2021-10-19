"""
Contains a dct with regular expressions (regexes). It is imported by
the parser.py script to find vars in the raw text of the press-release.

Each key-value pair represents:
{
    # regex description
    regex_name : <raw regex> # raw string with future regular expression
}

Actual regular expression would be build by:

(import re)
the_regex = re.compile(<raw regex>, re.DOTALL)
value = the_regex.findall[0]

The '|' symbol is used to present a number of distinct variants of 
a regex:

<variant 1> | <variant 2> | <variant 3>

In this case output of <<the_regex.findall[0]>> would be a tuple. So
parser.py has a <<choose_value>> static method to deal with 
('', '<value>', '') tuple to fetch a <value> from it.

RUSSIAN SUMMARY:
В файле приводится словарь с регулярными выражениями. С его помощью скрипт
parser.py ищет нужные переменные в тексте релиза.
"""

regexes = {
            
          # новые случаи COVID-19 в России за сутки
          'russia_new_cases' :
            
          '|'.join((
          r'случа\w+ коронавирусной инфекции COVID\W19\s?–\s(\d+\s?\d+) в \d+ рег',
          r'случа\w+ новой коронавирусной инфекции COVID\W19\s?–\s?(\d+\s?\d+) в \d+ рег',
          r'случа\w+ новой коронавирусной инфекции \(COVID\W19\)\s?–\s?(\d+\s?\d+) в \d+ рег'
          )),
           
          # прирост новых случаев в России за сутки в %
          'russia_current_pace' :
        
          r'\((\+.+%)\) коронавирусной инфекции в \d+',
           
          # число смертей в России за сутки
          'russia_new_deaths' :
            
          '|'.join((
          r'За последние сутки умер\w+ (\d+) челове',
          r'Умерл\w за последние сутки (\d+) челове',
          r'За последние сутки подтвержден\w? {1,3}(\d+\s?\d+) {1,3}летальн\w+ случа',
          r'За последние сутки подтвержден\w? {1,3}(\d+\s?\d+) {1,3}смерт'
          )),
           
          # число выздоровевших в России за сутки
          'russia_new_recovered' :

          '|'.join((
          r'За последние сутки выписан\w? (\d+\s\d+)\s+челов',
          r'За прошедшие сутки выписан\w? по выздоровлени\w\s{1,3}(\d+\s?\d+) {1,3}человек'
          )),
           
          # общая сумма случаев COVID-19 в России за все время
          'russia_total_cases' :

          '|'.join((
          r'Российской Федерации нарастающим итогом зарегистрирован\w* (\d+\s?\d+\s?\d+)\s?случа',
          r'России нарастающим итогом зарегистрирован\w* (\d+\s?\d+\s?\d+)\s?случа',
          r'В Российской Федерации нарастающим итогом зарегистрирован\w? (\d+\s?\d+\s?\d+)\s?случа'
          )),
           
          # число новых случаев в Москве за сутки
          'moscow_new_cases' :

          '|'.join((
          r'Распределение по субъектам.*Москва\s\W?\s?(\d+).*В Российской Федерации нарастающ',
          r'Распределение по субъектам.*Москва\s\W?\s?(\d+).*В России нарастающ'
          )),
        
          # число смертей в Москве за сутки
          'moscow_new_deaths' :

          '|'.join((
          r'За последние сутки умер\w* {1,3}\d+\s?\d+ {1,3}человек.*Москва\s+\W?\s?(\d+).*Умер\w* за весь период',
          r'Умер\w* за последние сутки {1,3}\d+\s?\d+ {1,3}человек.*Москва\s+\W?\s?(\d+).*За весь период умерл',
          r'Умер\w* за последние сутки {1,3}\d+\s?\d+ {1,3}человек.*Москва\s+\W?\s?(\d+).*Умер\w* за весь период',
          r'За последние сутки умер\w* {1,3}\d+\s?\d+ {1,3}человек.*Москва\s+\W?\s?(\d+).*За весь период умерл',
          r'.*'.join((
                    r'За последние сутки подтвержден\w+ {1,3}\d+\s?\d+ {1,3}летальн\w+ случа',
                    r'Москва\s+\W?\s?(\d+)',
                    r'За весь период по России умер'
                    )),
          r'.*'.join((
                    r'За последние сутки подтвержден\w? {1,3}\d+\s?\d+ {1,3}смерт',
                    r'Москва\s+\W?\s?(\d+)',
                    r'За весь период по России умер'
                    ))
          )),
           
          # число выздоровевших в Москве за сутки
          'moscow_new_recovered' :

          '|'.join((
          r'.*'.join((
                    r'За последние сутки выписан\w*.*человек\w?',
                    r'Москва\s+\W?\s?(\d{3,6})',
                    r'За весь период выписан'
                    )),
          r'.*'.join((
                    r'За последние сутки выписан\w*.*человек\w?',
                    r'Москва\s+\W?\s?(\d{3,6})',
                    r'Выписан\w* за весь'
                    )),
          r'.*'.join((
                    r'За прошедшие сутки выписан\w? по выздоровлени\w\s{1,3}\d+\s?\d+ {1,3}человек',
                    r'Москва\s+\W?\s?(\d{3,6})',
                    r'За весь период выписан'
                    ))
          )),
        
          # "золотая цитата" 
          'golden_cite' :
        
          r'(За последние сутки в.*без клинических проявлений)',
           
          # общее число смертей от COVID-19 в России за все время
          'russia_total_deaths' :

          '|'.join((
          r'За весь период умер\w+\s+(\d+\s?\d+)\s+челов',
          r'Умер\w* за весь период (\d+\s?\d+) челов',
          r'За весь период по России умер\w+ (\d+\s?\d+) человек',
          r'За весь период по России умер\w? (\d+\s?\d+) чел',
          r'За весь период по России умерл\w {1,6}(\d+\s?\d+) {1,3}человек'
          )),
           
          # общее число выздоровевших в России за все время
          'russia_total_recovered' :

          '|'.join((
          r'За весь период выписан\w+\s+(\d+\s?\d+\s?\d+)',
          r'За весь период выписано по выздоровлени\w {1,2}по России\s+–?\s{0,3}(\d+\s?\d+\s?\d+)'
          ))
        }
