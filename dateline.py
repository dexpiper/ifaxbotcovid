"""
This module rovides Dateline class to construct date and weekday
strings in Russian like '16 июля' and 'в четверг' using system time.

Usage:
dl = Dateline()
date_dateline, date_day = dl.dateline, dl.weekday

"""

from time import time, strftime, gmtime

class Dateline():

    """
    Takes day, day of the week and month from system time 
    and provides ready-to-use strings like '16 июля' and
    'в четверг' for dateline paragraph.

    Класс берет из системного времени день, месяц и день недели
    и дает готовые строки с датой и днем недели,
    например: "16 июля" и "в четверг".
    """

    def __init__(self):
        self._thetime = gmtime(time() + 10800)         # для новостей используется МСК (+3 часа)
        self._weekday = strftime('%w', self._thetime)
        self._month = strftime('%m', self._thetime)
        self._day = strftime('%d', self._thetime)
        if self._day.startswith('0'):
            self._day = self._day[1:]
        self.dateline = self._day + ' ' + self._month_name(self._month)
        self.weekday = self._weekday_name(self._weekday)
    
    @staticmethod
    def _month_name(arg: str):
        """
        Возвращает название месяца в род. падеже
        """
        arg = str(int(arg))
        month_names = ('января', 'февраля', 'марта', 'апреля',
        'мая', 'июня', 'июля', 'августа', 'сентября', 'октября',
        'ноября', 'декабря')
        month_dct = {                                  # словарь вида '1' : 'января'
            str(int(number) + 1) : month_names[number]
            for number in range(len(month_names))
            }
        return month_dct[arg]
    
    @staticmethod
    def _weekday_name(arg: str):
        """
        Возвращает название дня недели с предлогом
        """
        weekdays = ('в воскресенье', 'в понедельник', 'во вторник',
        'в среду', 'в четверг', 'в пятницу', 'в субботу'
        )
        weekdays_dct = {#словарь вида '0' : 'воскресенье'
            str(int(number)) : weekdays[number]
            for number in range(len(weekdays))
            }
        return weekdays_dct[arg]

# for testing only
if __name__ == '__main__':
    date = Dateline()
    lines = 'Москва. {}. ИНТЕРФАКС - \n- {}.'.format(date.dateline, date.weekday)
    print(lines)
    print(strftime('%H %M %S', date._thetime))