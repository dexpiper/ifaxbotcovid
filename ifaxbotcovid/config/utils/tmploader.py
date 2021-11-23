import logging


path = 'ifaxbotcovid/config/templates/'


def gettexttemplate():
    try:
        with open(path + 'texttemplate.txt', 'r') as file:
            t = file.read()
    except FileNotFoundError:
        logging.error('File for text template not found')
        return 'Шаблон текста не найден'
    return t


def getflashtemplate():
    try:
        with open(path + 'flashtemplate.txt', 'r') as file:
            f = file.read()
    except FileNotFoundError:
        logging.error('File for flash template not found')
        return 'Шаблон флэша не найден'
    return f


def getrpntemplate():
    try:
        with open(path + 'rpntemplate.txt', 'r') as file:
            rpn = file.read()
    except FileNotFoundError:
        logging.error('File for RPN template not found')
        return 'Шаблон РПН не найден'
    return rpn
