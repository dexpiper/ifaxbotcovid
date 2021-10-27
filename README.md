# ifaxBotCovid - reporter's helper

Currently available at https://t.me/ifaxcovidbot.

### Table of contents
1. [Introduction](#introduction)
2. [Technologies and libraries](#technologies-and-libraries)
3. [Scope of functionalities](#scope-of-functionalities):
* [Parser](#core:-parser)
* [Intermediate logic](#intermediate-logic:-covidchef)
4. [Examples of use](#examples-of-use)
5. [Project structure](#structure)
6. [Sources](#sources)
7. [Further development](#further-development)

***

### Introduction

Simple Telegram bot. Helps journalists to fetch data from Russian daily COVID-19 official press-releases and write news materials on their basis since October, 2020. Initialized by journalist for fellow colleagues from Interfax News Group (Moscow) to save time when dealing with the daily routine. The bot neither stores data, nor pulls any from the web - it just parses the sent text and fills the pre-written form:

> user sends text *==>*
> bot finds variables and organizes them *==>*
> bot fills templates with found variables *==>*
> bot sends back ready news material.

You can test the bot out with any of sample press-releases from *ifaxbotcovid/tests/test_data* folder of this repo. The ones with "corrupted" in names would yeild an error.

* Bot is settled to find *11 variables* in the COVID-19 press-release, issued by Russian authorities: the numbers of registered COVID patients, COVID-related deaths and recovered patients in Russia and in Moscow separately for the last 24 hours, total sum of this variables since the start of the pandemic etc. 
* Also bot re-writes long tables of new cases and deaths in the release, grouping regions by numbers of cases/deaths. Algorithm finds and detects the type of correspondent part of text, takes all the information into a dictionary and build ready text: region by region, string by string (implemented in *ifaxbotcovid.regioncounter*).
* All variables, found and generated, and ready re-written region tables go to the news material template. With all the gaps filled, ready news material is stamped out to the user.

### Technologies and libraries

Project is created with:

* Python 3.8.2
* [pyTelegramBotAPI 3.7.9](https://github.com/eternnoir/pyTelegramBotAPI)
* Flask/gunicorn for handling and forwarding requests
* pytest (tests), venv (virtual environment), Git (version control)

* Key functionality (finding values in text) heavily depends on the *re* module from the Standard Library that provides regular expression operations.

* The bot runs at *Heroku*, pipelined directly from the main brunch of this repository.

### Scope of functionalities

#### Core: Parser

- The core functionality is provided by *ifaxbotcovid.parser.texparser* module.

- Textparser finds values essential for the future news material with pre-written regular expressions (the *re* module from the Standard Python Library). Regexes are defined in [*ifaxbotcovid.config.regex* module](https://github.com/dexpiper/ifaxbotcovid/blob/5363811584cac8b1266953a2e9e23576c96a9d47/ifaxbotcovid/config/regex.py). Bot is designed to deal with some deviations in press-release text, so most of the variables have 2-3 regexes to try.

**Variables to find**:
   - COVID cases ----------- \
   - COVID deaths ------------ *in Moscow and in Russia registered officially for the last 24h*
   - recovered patients ---- /
   - total number of cases ------ \
   - total number of deaths ----- *in Russia, since the start of the pandemic*
   - total number of recovered -- /
   - growth rate ("pace")
   - quotation from the start of the release

**Variables to generate**:
   - Active cases = total cases - (total deaths + total recovered)
   - Dateline and name of day of the week (from *time.time* with respect to morphological form and preposition in Russian language)
   - Re-written tables about other regions statistics

- All the found variables and ready region blocks fit into patterns in the *ifaxcovidbot.config.schemes*. In the outcome, bot gets a ready-to-use news material and sends it to the user.
- If the message with the raw text had a 'йй' symbols in the end, bot also provides the user with a log of the operations performed. Log is meant to be sent in a separate message.
- Bot programmed to warn user if some of the variables are suspiciously small (defined in *ifaxcovidbot.config.settings*). Also user will get a notice if some of the variables haven't been found (a gap would be filled with a *NO_VALUE* dummy).

**Addition feature**
Bot also can parse a short piece of text provided daily by the press-office of the RPN (Russian Federal agency in charge of virus protection, Rospotrebnadzor), containing information about COVID tests performed in Russia.

- If bot detects this kind of text in incoming message (it is a simple and rather small string), it finds 3 variables in it:
  + total number of tests, 
  + tests done for the last 24 h, 
  + peoples under the medical monitoring

- Then puts variables into template (*ifaxbotcovid.config.settings*) and gives the user ready-to-use block of text in the answer message.

This feature, realized in *ifaxbotcovid.rpn*, is pretty streightforward. All the regular expressions for it defined in the named module, not in *ifaxbotcovid.config.regex*.

#### Intermediate logic: CovidChef

Bot acts like a tiny web app written in Flask, getting new Telegram messages via webhook. When a message recieved, Flask routes redirects it to Telebot (pyTelegramBotAPI), who should call correspondent internal module and send ready template with all the mined data inside.

Telegram <==> Flask <=> Telebot <=> Parser

The idea behind the bot was its straightforwardness and simplicity: user just sends text and recieves ready material in bot answer - no commands, no files, no settings. This approach raised several problems:

- Telegram tends to cut long messages sent to a bot into several pieces, but *ifaxbotcovid.parser.textparser* should get them all in one piece.
- *ifaxbotcovid* should destinguish raw COVID-19 press-release from short COVID-test report provided by Russian agency RPN. Also bot should ignore any messages that are not press-releases and RPN reports.

Firstly, COVID-19 official press releases in Russia were rather short - Telegram used to cut them in just in two pieces. But in the fall of 2021 the everyday pandemic statistics has become more detailed, thus I have to re-write previous code and add new structure element - an intermediate logic between Telebot and internal scripts:

Telegram <======> Flask <=> Telebot <=> CovidChef <=> Parser

CovidChef is organized as a custom Python class, initialized along with the Flask and Telebot. In general:

1) Telebot gives any recieved message to the Chef
2) Chef does its magic
3) Telebot sends Chef's answers back to user

Under the bonnet Chef stores messages in fast temporary MessageStorage (using deque), glues sequential messages from single user with certain context (defined in *ifaxbotcovid.config*) together and calls *ifaxcovidvbot.parser.textparser* when glued text seems completed and ended. The Chef's answer is organized in separate class with special flag. This flag signals when the last message were properly cooked to send ready answer to user. Also Chef rapidly cooks short RPN report when recieved one, calling *ifaxbotcovid.parser.rpn*.

**Environment variables**

Two env vars should be defind:
- Telegram bot *TOKEN* (from BotFather)
- *URL* where Telegram would send messages

Webhook should be registered manualy by "*URL*/setwebhook" request.
Token for testing purposes could be defined in *ifaxbotcovid.config.token.TOKEN*

**Templates**

Templates are stored in *ifaxbotcovid/config/schemes*. Any other templates could be used instead of the default ones, placeholders for variables are defined in curly brackets:

```
Some text here: {name_of_variable1}, {name_of_variable2}.
Another piece of text
etc.
```

Names of variables and their descriptions are listed in the file.

***

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

Outcome with default template:
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

### Structure

```
/
wsgi.py                    - *Flask routes, Telebot handlers, Chef instance creation*
manual_parse.py            - *manual testing for textparser.py*
manual_rpn_parse.py        - *manual testing for rpn.py*

  /ifaxbotcovid
    
    /bot
        logic.py               - *CovidChef to call parsers and to bring answers*
        helpers.py             - *CovidChef helpers*
        factory.py             - *Flask, Telebot and Chef starts here*

    /parser

        textparser.py          - *chief module for parsing the big release*
        rpn.py                 - *module for parsing short RPN report*
        ...

    /config
        regex.py               - *regular expressions used by the 'textparser.py'*
        schemes.py             - *templates*
        settings.py            - *admins, some base vars and key words defined here*
        startmessage.py        - *message to answer /start command*

  /tests
    ...
    /unit_tests
    /test_data

        sample_xxx.txt     - *input for test, .txt files > 300 considered as a textparser.py input, less then 300 - as a rpn.py input. Any "sample_xxx.txt" content can be used as a valid input for telegram bot*

        corrupted_xxx.txt  - *files with "corrupted" in their name deliberately placed to raise an error during the tests*
        ...
```

### Sources
The project is inspired by:
* [the guide](https://tproger.ru/translations/telegram-bot-create-and-deploy/) on tproger website 
* [Automate the boring staff with Python](https://automatetheboringstuff.com/) by Al Sweigart
* [Fluent Python](https://www.oreilly.com/library/view/fluent-python/9781491946237/) by Luciano Ramalho
* My grateful collegues

Firstly written for personal use as a bunch of Python scripts called via command line, later the staff transformed into a simple, but fast and pretty straightforward solution for fellow Interfax reporters.

### Further development
Having a working parsing algorithm and a bot to launch it, it is rather simple to change ready patterns for putting values into. That means the bot could be tuned to necessities of a vast circle of editors and journalists, both in Russia and outside the country.
