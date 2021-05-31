'''
The file contains patterns - blocks of text with gaps where new information
could be inserted. Every piece of information has a named variable for it.

List of avaliable variables:

### FOR COVID-19 DAILY RELEASE

russia_new_cases        # new COVID-19 cases in Russia for the last 24h 
russia_current_pace     # difference of total COVID-19 cases in % between today and yesterday
russia_new_deaths       # COVID-related deaths in Russia for the last 24h
russia_new_recovered    # patients recovered after COVID for the last 24h
russia_total_cases      # total COVID-19 cases in Russia for present
russia_total_deaths     # total COVID-related deaths in Russia for present
russia_total_recovered  # total number of patients recovered after COVID-19 in Russia
russia_active           # active COVID cases: <total cases> - (<total recoverd> + <total dead>)
moscow_new_cases        # Moscow COVID-19 cases for 24h
moscow_new_deaths       # Moscow COVID-related deaths for 24h
moscow_new_recovered    # Moscow recovered COVID-patients for 24h 

date_dateline           # formatted date and month for dateline string in Russian ("12 января") 
date_day                # day of the week in Russian put in right grammatical form
golden_cite             # a piece of original raw text for the second paragraph

### FOR RPN COVID-TESTING DAILY MESSAGE

'total_tests'           # total number of COVID-19 tests performed in Russia
'recent_tests'          # number of COVID tests for the last 24h
'people_monitored'      # number of patients under medical control after COVID contact

'''

###
### pattern for flash - urgent news agency's message
###
flash = '''ЭМБАРГО

МОЛНИЯ
В РФ ВЫЯВЛЕНО {russia_new_cases} НОВЫХ СЛУЧАЕВ ЗАРАЖЕНИЯ COVID-19 ЗА СУТКИ ({russia_current_pace}), {russia_new_deaths} ПАЦИЕНТОВ СКОНЧАЛИСЬ, {russia_new_recovered} ТЫС. ВЫПИСАНЫ ИЗ БОЛЬНИЦ – ОПЕРШТАБ
1**

МОЛНИЯ
В МОСКВЕ ВЫЯВЛЕНО {moscow_new_cases} НОВЫХ СЛУЧАЕВ ЗАРАЖЕНИЯ КОРОНАВИРУСОМ ЗА СУТКИ, {moscow_new_deaths} ПАЦИЕНТОВ СКОНЧАЛИСЬ, {moscow_new_recovered} ВЫПИСАНЫ ИЗ БОЛЬНИЦ – ОПЕРШТАБ
1**
'''

###
### pattern for ordinary news message text
###
text = '''
ЭМБАРГО

ЭКСПРЕСС-РОССИЯ-COVID-СТАТИСТИКА
{russia_new_cases} тыс. новых случаев COVID-19 в РФ, {russia_new_deaths} умерших - оперштаб
Москва. {date_dateline}. ИНТЕРФАКС - Суточный прирост новых заболевших коронавирусной инфекцией составил {russia_new_cases} тыс. случаев, умерли за сутки {russia_new_deaths} пациентов, следует из данных оперативного штаба, обнародованных {date_day}.
"{golden_cite}", - говорится в сообщении штаба.
Нарастающим итогом в России зарегистрировано {russia_total_cases} случаев коронавирусной инфекции, {russia_total_deaths} умерших и {russia_total_recovered} выписанных ({russia_new_recovered} выписаны за последние сутки). Таким образом, общее количество активных случаев в стране (общее число случаев за вычетом всех выздоровевших и всех умерших) на текущий момент составляет {russia_active}.
В Москве {date_day}, сообщает оперативный штаб, {moscow_new_cases} новых случаев COVID-19 за сутки, {moscow_new_deaths} смертей и {moscow_new_recovered} выздоровевших.
ПОКАЗАТЕЛИ ПРИРОСТА И СМЕРТНОСТИ В РЕГИОНАХ
{ready_cases}
{ready_deaths}
1** ЭМБАРГО'''

###
### pattern for RPN COVID-testing daily message
###
rpn = '''ТЕСТИРОВАНИЕ
По информации Роспотребнадзора, опубликованной {date_day}, в России нарастающим итогом проведено более {total_tests} млн тестов на COVID-19, из них {recent_tests} тыс. - за последние сутки. Под медицинским наблюдением в стране остается {people_monitored} человек.
'''