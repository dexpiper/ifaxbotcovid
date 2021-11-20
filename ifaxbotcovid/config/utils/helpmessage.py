import logging


def helpmsg():
    try:
        with open('ifaxbotcovid/config/messagehelp.txt', 'r') as file:
            h = file.read()
    except FileNotFoundError:
        logging.warning('File for helpmessage has not been found')
        h = 'Welcome to ifaxbotcovid!'
    return h
