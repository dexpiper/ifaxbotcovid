import logging


def startmsg():
    try:
        with open('ifaxbotcovid/config/messagestart.txt', 'r') as file:
            s = file.read()
    except FileNotFoundError:
        logging.warning('File for startmessage has not been found')
        s = 'Welcome to ifaxbotcovid!'
    return s
