'''
Tests textparser.py functionality along with its dependencies
'''

from dataclasses import dataclass
from pathlib import Path

import pytest
from ifaxbotcovid.parser import tables, textparser
from ifaxbotcovid.config.utils.settings import base_vars
from tests import instruments as inst


@pytest.fixture
def samples():

    @dataclass
    class Sample:
        # sample vars for testing
        sample = 'Тридцать тысяч обезьян'
        sample2 = ' Foo bar  '
        sample_dict = {'Foo': 'bar', 'Hello': 'world!'}
        big_sample = inst.Instruments.get_text_from_file(
            Path('tests/test_data/sample_text.txt')
            )

    return Sample


@pytest.fixture
def parser(samples):
    return textparser.Parser(samples.sample)


class TestUnitParser:

    def test_NAcounter(self, parser):
        count = parser.NAcounter()
        assert count == 12, "Function doesn't work correctly"

    def test_del_space(self, parser, samples):
        result = parser.del_space(samples.sample2)
        assert result == 'Foobar'

    def test_get_key(self, parser, samples):
        result = parser.get_key(
            samples.sample_dict, 'world!'
        )
        assert result == 'Hello'

    class TestTableDetection:

        def test_find_tables(self, samples):
            ready_cases, ready_deaths, tlog = tables.tables(
                samples.big_sample,
                short=100
                )
            condition1 = ready_cases.startswith(
                'По информации оперативного штаба, еще'
            )
            condition2 = ready_deaths.startswith(
                'Согласно данным оперштаба о смертности,'
            )
            condition3 = 'Ошибка' not in tlog

            should_be_true = (
                condition1 and condition2 and condition3
            )

            assert should_be_true, 'Failed to detect tables'

    class TestVars:

        def test_vars_finding(self, samples):
            _, _, parser = inst.Instruments.parse(
                samples.big_sample,
                get_parser=True  # getting the parser object for analysis
                )
            values = parser.values
            expected_values = {
                'russia_new_cases': '7920',
                'russia_current_pace': '+0,16%',
                'russia_new_deaths': '390',
                'russia_new_recovered': '9561',
                'russia_total_cases': '4965676',
                'moscow_new_cases': '2096',
                'moscow_new_deaths': '61',
                'moscow_new_recovered': '2663',
                'russia_total_deaths': '116965',
                'russia_total_recovered': '4581787'
                }
            errors = 0
            failed_keys = []
            for key in expected_values.keys():
                if values[key] != expected_values[key]:
                    errors += 1
                    failed_keys.append(key)
            assert errors == 0,\
                f'Did not found values. Failed keys: {str(failed_keys)}'

        def test_fool_check(self, parser):

            total_cases = int(base_vars['russia_total_cases']) + 1
            total_deaths = int(base_vars['russia_total_deaths']) + 1
            total_recovered = int(base_vars['russia_total_recovered']) + 1

            good_dct = {
                'russia_new_cases': '7920',
                'russia_current_pace': '+0,16%',
                'russia_new_deaths': '390',
                'russia_new_recovered': '9 561',
                'russia_total_cases': str(total_cases),
                'moscow_new_cases': '2096',
                'moscow_new_deaths': '61',
                'moscow_new_recovered': '2663',
                'date_dateline': '7 июня',
                'date_day': 'в понедельник',
                'golden_cite': 'Большая и длинная цитата',
                'russia_total_deaths': str(total_deaths),
                'russia_total_recovered': str(total_recovered),
                'russia_active': '99999',
                }

            bad_dct = good_dct.copy()
            bad_dct['russia_total_cases'] = str(total_cases - 3)
            bad_dct['russia_total_deaths'] = str(total_deaths - 3)
            bad_dct['russia_total_recovered'] = str(total_recovered - 3)

            condition1 = parser.fool_check(good_dct)
            condition2 = parser.fool_check(bad_dct)

            assert not condition1, "Mistake found where shouldn't be one"
            assert condition2, "Failed to detect error"
