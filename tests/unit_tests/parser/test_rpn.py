'''
Tests rpn.py functionality, uses .txt files from tests/test_data
folder < 300 symbols long as valid input.

'''

from pathlib import Path

from tests import instruments as inst


class NoFileError(Exception):
    pass


class NoExpectedVarTypeError(Exception):
    pass


class TestRPN:

    data_folder = Path('tests/test_data/')
    files = []
    good_rpn_files = []

    def test_check_rpn_files(self):
        TestRPN.files = inst.Instruments.import_files(TestRPN.data_folder)
        assert len(TestRPN.files) > 0, 'No text files in tests/test_data'
        for file in TestRPN.files:
            raw_text = inst.Instruments.get_text_from_file(file)
            if len(raw_text) < 300:
                TestRPN.good_rpn_files.append(file)
        assert len(TestRPN.good_rpn_files) > 0, 'No file to use in parser test'

    def test_parse_rpn_files(self):

        if len(TestRPN.good_rpn_files) == 0:
            raise NoFileError('No good text files to check RPN-parser found')

        for file in TestRPN.good_rpn_files:
            rawtext = inst.Instruments.get_text_from_file(file)
            text, log = inst.Instruments.parse_rpn(rawtext)

            if type(text) == tuple:
                raise NoExpectedVarTypeError

            condition = (
                'NO_VALUE' not in text
                ) and (
                'не удалось' not in log
                )

            # 'corrupted' in file name indicates the text
            # should not pass the condition
            if 'corrupted' in file.stem:
                err = f'Corrupted {file.name} should raise an exception'
                assert condition is False, err

            # in other cases condition should evaluate as True
            else:
                assert condition, f'File {file.name} did not pass the test'
