# ifaxBotCovid - reporter's helper

Currently available at https://t.me/ifaxcovidbot, deployed at Heroku.

### Table of contents
* [Introduction](#introduction)
* [Technologies and libraries](#technologies-and-libraries)
* [Scope of functionalities](#scope-of-functionalities)
* [Examples of use](#examples-of-use)
* [Sources](#sources)
* [Further development](#further-development)

### Introduction

Simple Telegram bot. Helps journalists to fetch data from daily COVID-19 official press-releases and write news materials on their basis. Initialized by journalist for fellow colleagues from Interfax News Group (Moscow) to save time when dealing with the daily routine. The bot neither stores data, nor pulls any from the web - it just parses the sent text and fills the pre-written form.

### Technologies and libraries

Project is created with:
* Python 3.8.2
* [pyTelegramBotAPI 3.7.3](https://github.com/eternnoir/pyTelegramBotAPI)

Also *pyperclip* for testing internal modules.

### Scope of functionalities

**General function**
- User sends the press-release as a simple message to the bot. Every message long enough to be the COVID-19 release would be considered as a source text. First, bot glues two sequential messages (sent less then 1 sec from each other). Then it gives the raw text to the Parser (*parser. py*). 
- Parser finds values essential for the future news material with pre-written regexes (the *re* module from the Standard Python Library). It is the number of new COVID-19 cases registered officially in Russia, new deaths, and new patients who were considered as recovered. Also Parser searches for other variables such as total cases, total deaths, total recovered, number of cases, deaths and recovered persons in Moscow, a piece of text for the cite in the future news material etc. 
- Also Parser calls *Tables. py* module for processing long lists of Russian regions and their cases and deaths. Out comes nicely sorted and transformed blocks of text (*RegionCounter. py*).
- All the found variables and ready region blocks fit into patterns in the *schemes. py*. In the outcome, bot gets a ready-to-use news material and sends it to the user.
- If the message with the raw text had a 'йй' symbols in the beginning or in the end, bot also provides the user with a log of the operations performed.

**Second function**
- Bot also can parse a short piece of data provided daily by the press-office of the RPN (Russian Federal agency in charge of virus protection), containing information about COVID tests.
- If bot detects this kind of text in incoming message, it gives the user ready-to-use block of text in the answer message.

### Examples of use

Raw press release:
```Оперативная сводка на 30.10.2020
За последние сутки в России подтвержденных случаев новой коронавирусной инфекции COVID-19 – 18283 в 84 регионах, в том числе выявлено активно 4072 (22,3%) без клинических проявлений. 

Распределение по субъектам
1	Москва	5268
2	Санкт-Петербург	801
3	Московская область	524
 <...>
 В Российской Федерации нарастающим итогом зарегистрировано 1 599 976 случая (+1,2%) коронавирусной инфекции в 85 регионах.

За последние сутки подтверждено  355 летальных случаев:
Воронежская область	1
Ивановская область	3
Калужская область	3
Костромская область	1
Курская область	4
Липецкая область	1
Московская область	13
<...>
Амурская область	2
Хабаровский край	2
За весь период по России умерло  27 656 человек.

За прошедшие сутки выписано по выздоровлению  14 519 человек: 
Белгородская область	128
Брянская область	56
Владимирская область	78
<...>
Хабаровский край	68
Сахалинская область	110
Чукотский автономный округ	1
За весь период выписано по выздоровлению по России  –  1 200 560
```

Outcome:
```ЭМБАРГО

МОЛНИЯ
18283 НОВЫХ СЛУЧАЕВ COVID-19 В РФ (+1,2%), 355 УМЕРШИХ, 14,52 ТЫС. ВЫПИСАННЫХ – ОПЕРШТАБ

МОЛНИЯ
В МОСКВЕ 5268 НОВЫХ СЛУЧАЕВ КОРОНАВИРУСА, 69 СМЕРТЕЙ, 3985 ВЫПИСАННЫХ – ОПЕРШТАБ
ЭМБАРГО

ЭМБАРГО

ЭКСПРЕСС-РОССИЯ-COVID-СТАТИСТИКА
18,28 тыс. новых случаев COVID-19 в РФ, 355 умерших - оперштаб
Москва. 30 октября. ИНТЕРФАКС - Суточный прирост новых заболевших коронавирусной инфекцией составил 18,28 тыс. случаев, умерли за сутки 355 пациентов, следует из данных оперативного штаба, обнародованных в пятницу.
"За последние сутки в России подтвержденных случаев новой коронавирусной инфекции COVID-19 – 18283 в 84 регионах, в том числе выявлено активно 4072 (22,3%) без клинических проявлений", - говорится в сообщении штаба.
Нарастающим итогом в России зарегистрировано 1599976 случаев коронавирусной инфекции, 27656 умерших и 1200560 выписанных (14519 выписаны за последние сутки). Таким образом, общее количество активных случаев в стране (общее число случаев за вычетом всех выздоровевших и всех умерших) на текущий момент составляет 371760.

ПОКАЗАТЕЛИ ПРИРОСТА И СМЕРТНОСТИ В СТОЛИЦЕ И РЕГИОНАХ
В Москве в пятницу, сообщает оперативный штаб, 5268 новых случаев COVID-19 за сутки, 69 смертей и 3985 выздоровевших.
По информации оперативного штаба, еще 801 новых случаев COVID-19 зафиксировано в Санкт-Петербурге, 524 - в Московской области, 401 - в Нижегородской области, 325 - в Архангельской области, 310 - в Ростовской области, 296 - в Воронежской области, 292 - в Красноярском крае, 284 - в Свердловской области, по 232 - в Иркутской области, Забайкальском крае. 231 - в Коми, 224 - в Хабаровском крае, 219 - в Алтайском крае, 216 - в Крыму, 215 - в Бурятии, <...> 151 - в Челябинской области, В других регионах России суточный прирост не превышает 150.

Согласно данным оперштаба о смертности, 69 пациентов скончалось за сутки в Москве, 36 - в Санкт-Петербурге, 15 - в Ростовской области, по 13 летальных случаев в Московской области, Нижегородской области. По 8 умерших в Республике Алтай, Бурятии, Якутии, Иркутской области, Красноярском крае. <...> По 2 - в Крыму, Кабардино-Балкарии, Амурской области, Орловской области, Тульской области, Пензенской области, Челябинской области, Хабаровском крае, Севастополе. По 1 - в Башкирии, Марий Эл, Мордовии, Татарстане, Калининградской области, Кировской области, Воронежской области, Костромской области, Липецкой области, Рязанской области. 
1** ЭМБАРГО
```

### Sources
The project is inspired by:
* [the guide](https://tproger.ru/translations/telegram-bot-create-and-deploy/) on tproger website 
* [Automate the boring staff with Python](https://automatetheboringstuff.com/) by Al Sweigart
* Fluent Python book by Luciano Ramalho
* different Git guides and tutorials

Firstly written for personal use as a bunch of Python scripts called via command line, now the staff transformed into a simple, but fast and pretty straightforward solution for Interfax reporters.

### Further development
Having a working parsing algorithm and a bot to launch it, it is rather simple to change ready patterns for putting values into. That means the bot could be tuned to necessities of a vast circle of editors and journalists, both in Russia and outside the country.