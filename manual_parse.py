import pprint
import pyperclip

from ifaxbotcovid.parser import textparser as p

if pyperclip.paste is not None:
    rawtext = pyperclip.paste()
    parser = p.Parser(rawtext)
    text = parser()
    if type(text) == tuple:
        for el in text:
            print(el)
    else:
        print(text)
    pprint.pprint(parser.log)
