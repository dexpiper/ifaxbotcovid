from dataclasses import dataclass
import logging

import pytest

from ifaxbotcovid.parser.utils import ParserHelpers
from ifaxbotcovid.config.settings import boundary


@pytest.fixture
def samples():

    @dataclass
    class Samples:
        sample = 'Тридцать тысяч обезьян'
        sample2 = ' Foo bar  '
        sample_dict = {'Foo': 'bar', 'Hello': 'world!'}
        sample_tuple = ('', 'Foo', '')
        sample_tuple2 = ('', 'Foo', '', 'bar')
        sample_tuple3 = ('Foo')

    return Samples


class TestChooseValue:

    def test_choose_value1(self, samples):
        result = ParserHelpers.choose_value(
            samples.sample_tuple
        )
        assert result == 'Foo'

    def test_choose_value2(self, samples):
        result = ParserHelpers.choose_value(
            samples.sample_tuple2
        )
        assert result == 'Foo'

    def test_choose_value3(self, samples):
        result = ParserHelpers.choose_value(
            samples.sample_tuple3
        )
        assert result == 'Foo'

    def test_choose_value4(self, samples):
        result = ParserHelpers.choose_value(
            samples.sample
        )
        assert result == samples.sample


class TestComma:

    def test_comma1000(self):
        result = ParserHelpers.comma1000('123456')
        assert result == '123,46'

    def test_comma(self):
        result = ParserHelpers.comma('1234.56')
        assert result == '1234,56'


class TestChangeShape:

    def test_change_shape(self):
        result = ParserHelpers.change_shape('1098007')
        assert result == '1 млн 098 тыс. 007'

    def test_change_shape2(self):
        result = ParserHelpers.change_shape('10376')
        assert result == '10 тыс. 376'

    def test_change_shape3(self):
        result = ParserHelpers.change_shape('376')
        assert result == '376'

    def test_change_shape_caps(self):
        result = ParserHelpers.change_shape('1091006', caps=True)
        assert result == '1 МЛН 091 ТЫС. 006'

    def test_change_shape_caps2(self):
        result = ParserHelpers.change_shape('10379', caps=True)
        assert result == '10 ТЫС. 379'


class TestCheckShort:

    def test_short_bad(self):
        result = ParserHelpers.check_short(2000)
        assert result == boundary.default

    def test_short_rounding(self):
        i = boundary.default + 2
        result = ParserHelpers.check_short(i)
        assert result == boundary.default

    def test_short_good(self):
        i = 400
        if i < boundary.lower or i > boundary.upper:
            logging.warning('Test data out of boundary set!')
            assert True
        else:
            result = ParserHelpers.check_short(i)
            assert result == i
