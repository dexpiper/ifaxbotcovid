import logging
import pprint
from logging.config import fileConfig

import pyperclip

from ifaxbotcovid.parser import textparser as p

fileConfig('ifaxbotcovid/config/logging.ini')
logger = logging.getLogger('parslogger')
logger.setLevel(logging.DEBUG)

if pyperclip.paste is not None:
    rawtext = pyperclip.paste()
    parser = p.Parser(rawtext, logger=logger)
    text = parser()
    if type(text) == tuple:
        for el in text:
            print(el)
    pprint.pprint(parser.log)
