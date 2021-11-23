import logging

from ifaxbotcovid.config.utils.settings import version


def startmsg():
    try:
        with open('ifaxbotcovid/config/messagestart.txt', 'r') as file:
            s = file.read()
    except FileNotFoundError:
        logging.warning('File for startmessage has not been found')
        s = 'Welcome to ifaxbotcovid!'
    return s.format(version=version)
