'''
A toolbox that contains common methods shared by the tests.

'''

from ifaxbotcovid.parser import rpn, textparser


class Instruments:

    @staticmethod
    def import_files(data_folder, suff='.txt'):
        files = [
            e for e in data_folder.iterdir() if
            (e.is_file() and (e.suffix == suff))
            ]
        return files

    @staticmethod
    def get_text_from_file(file):
        text = file.read_text()
        return text

    @staticmethod
    def parse(rawtext, get_parser=False):
        parser = textparser.Parser(rawtext)
        text = parser()
        log = parser.log
        if get_parser:
            return text, log, parser
        return text, log

    @staticmethod
    def parse_rpn(rawtext):
        constructor = rpn.RPN(rawtext)
        text, log = constructor.construct(), constructor.log
        return text, log
