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

    @staticmethod
    def check_html_tags(text):
        opened_tags = []
        opened_brackets = []
        tag = ''
        flag = False
        for i, symbol in enumerate(text):
            if symbol == '<':
                opened_brackets.append(symbol)
                flag = True
            elif symbol == '>':
                flag = False
                opened_brackets.pop()
                if len(opened_brackets):
                    raise AssertionError

                if tag.startswith('a '):
                    assert tag.count('href') < 2
                    tag = 'a'
                    opened_tags.append(tag)
                elif tag.startswith('/'):
                    tag = tag[1:]
                    if not len(opened_tags):
                        raise AssertionError(
                            f'No tags opened: {opened_tags}. '
                            f'Around: "{Instruments.around(text, i)}"'
                        )
                    if tag not in opened_tags:
                        raise AssertionError(
                            f'Tag {tag} has not been opened!'
                        )
                    else:
                        opened_tags.remove(tag)
                elif tag == '':
                    raise AssertionError('No tag')
                else:
                    opened_tags.append(tag)
                tag = ''
            elif flag:
                tag += symbol

        assert not len(opened_brackets)
        assert not len(opened_tags)
        return True

    @staticmethod
    def around(text, el_number, maxlen=12):
        assert maxlen > 0 and maxlen <= len(text), 'Invalid maxlen'
        result = []
        if (el_number - (maxlen - 1)) < 0:
            result.append(text[:el_number + 1])
            left = maxlen - len(''.join(result))
            if left > 0:
                for i in range(left, 0, -1):
                    try:
                        result.append(text[el_number:i])
                    except IndexError:
                        pass
        elif (el_number + maxlen - 1) > len(text):
            result.append(text[-el_number:])
            left = maxlen - len(''.join(result))
            if left > 0:
                for i in range(left, -0, -1):
                    try:
                        result.append(text[i:el_number])
                    except IndexError:
                        pass
        else:
            result.append(text[
                (
                    el_number - (round(maxlen/2) - 1)
                ):(
                    el_number + (round(maxlen/2) - 1)
                )
                ]
            )
        return ''.join(result)
