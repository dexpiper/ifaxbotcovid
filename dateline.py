''' Скрипт задает функцию TimeRus(), которая берет из системного времени
    день, месяц и день недели, и возвращает две строки с датой и
    днем недели, например: "16 июля" и "четверг"
'''

import datetime, pyperclip

def TimeRus():
    d = datetime.datetime.now().strftime('%d')
    m = datetime.datetime.now().strftime('%B')
    dw = datetime.datetime.now().strftime('%w')
    d = str(int(d))
    if m == 'January':
        m = 'января'
    elif m == 'February':
        m = 'февраля'
    elif m == 'March':
        m = 'марта'
    elif m == 'April':
        m = 'апреля'
    elif m == 'May':
        m = 'мая'
    elif m == 'June':
        m = 'июня'
    elif m == 'July':
        m = 'июля'
    elif m == 'August':
        m = 'августа'
    elif m == 'September':
        m = 'сентября'
    elif m == 'October':
        m = 'октября'
    elif m == 'November':
        m = 'ноября'
    elif m == 'December':
        m = 'декабря'
    if dw == '0':
        dw = 'воскресенье'
    elif dw == '1':
        dw = 'понедельник'
    elif dw == '2':
        dw = 'вторник'
    elif dw == '3':
        dw = 'среду'
    elif dw == '4':
        dw = 'четверг'
    elif dw == '5':
        dw = 'пятницу'
    elif dw == '6':
        dw = 'субботу'
    return str(d + ' ' + m), str(dw)

if __name__ == '__main__':
    date, dweek = TimeRus()
    lines = 'Москва. {}. ИНТЕРФАКС - \n- в {}.'.format(date, dweek)
    pyperclip.copy(lines)
