import re


class ParserHelpers:

    def comma1000(n, log=None):
        '''
        Делит на 1000, меняет точку на запятую, округляет (1234 => 1,23)
        '''
        try:
            n = round(int(n) / 1000, 2)
            regex1 = re.compile(r'\.')
            n = regex1.sub(',', str(n))
        except Exception:
            if log:
                log.append(
                    'Не удалось применить comma1000 к %s' % str(n)
                )
        return n

    def comma(n):
        '''
        Меняет точку на запятую (1.234 => 1,234)
        '''
        regex1 = re.compile(r'\.')
        n = regex1.sub(',', str(n))
        return n

    def change_shape(arg, log=None, caps=False):
        '''
        меняем '1098007' на строку '1 млн 098 тыс. 007'
        '''
        def zfill(x):
            '''
            '7' ==> '007'
            '''
            return str(x).zfill(3)

        try:
            # подстраховываемся на случай, если на входе будет NO_VALUE
            arg = int(arg)
        except Exception:
            if log:
                log.append(
                    'Не удалось применить change_shape к %s' % str(arg)
                )
            return str(arg)

        if arg > 1000000:

            millions = int(arg/1000000)
            thousands = int(arg/1000) - millions*1000
            hundreds = int(arg) - millions*1000000 - thousands*1000

            if caps:
                return '%s МЛН %s ТЫС. %s' % (
                    str(millions), zfill(str(thousands)), zfill(str(hundreds))
                )
            else:
                return '%s млн %s тыс. %s' % (
                    str(millions), zfill(str(thousands)), zfill(str(hundreds))
                )
        elif arg > 1000:
            thousands = int(arg/1000)
            hundreds = int(arg) - thousands*1000
            if caps:
                return '%s ТЫС. %s' % (str(thousands), zfill(str(hundreds)))
            else:
                return '%s тыс. %s' % (str(thousands), zfill(str(hundreds)))
        else:
            return str(arg)

    def choose_value(value):
        '''
        Функция сокращает tuple вида ('', 'цифра', '') до 'цифра'
        '''
        if type(value) == tuple:
            if len(value) > 1:
                for item in value:
                    if item == '':
                        None
                    else:
                        return item
                return ''
            else:
                return value[0]
        else:
            return value
