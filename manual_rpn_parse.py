import pprint
import pyperclip

from ifaxbotcovid import rpn as RPN_parser

if pyperclip.paste is not None:
    rawtext = pyperclip.paste()
    parser = RPN_parser.RPN(rawtext)
    text, log = parser.construct(), parser.log
    pprint.pprint(log)
    print(text)
