'''
Module asserts all the .txt files in tests/test_data folder could be read,
parsed and would yeild some result without errors.

- Any .txt file > 300 symbols long would be regarded as a valid
textparser.py text input. Files shorter then 300 reserved for rpn.py
text input.

- 'Corrupted' in .txt file name would be considered as a 'bad file' and
test would fail if the file had been processed without a 'NO_VALUE' in
the output.

'''

from pathlib import Path
import pprint
from tests import instruments as inst


class NoFileError(Exception):
    pass


class TestParser:

    data_folder = Path('tests/test_data/')
    files = []
    good_files = []

    def test_collect_files(self):
        TestParser.files = inst.Instruments.import_files(
            TestParser.data_folder
        )
        assert len(TestParser.files) > 0, 'No text files in tests/test_data'

    def test_check_files(self):
        if len(TestParser.files) == 0:
            raise NoFileError('No file to parse with textparser found')
        for file in TestParser.files:
            raw_text = inst.Instruments.get_text_from_file(file)
            if len(raw_text) > 300:
                TestParser.good_files.append(file)
        assert len(TestParser.good_files) > 0, 'No file to use in parser test'

    def test_parse_files(self):
        for file in TestParser.good_files:
            rawtext = inst.Instruments.get_text_from_file(file)
            text, log = inst.Instruments.parse(rawtext)

            # text var could be a tuple,
            # in this case we take last item as a text
            if type(text) == tuple:
                text = text[-1]

            condition = 'NO_VALUE' not in text

            # 'corrupted' in file name indicates the text
            # should not pass the condition
            if 'corrupted' in file.stem:
                m = f'Corrupted {file.name} did not raise exception'
                assert condition is False, m

            # regular file should pass the condition successfully
            else:
                assert condition, f'File {file.name} did not pass the test'
                pprint.pprint(log)
                print(text)
