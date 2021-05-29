'''
Tests textparser.py functionality along with its dependencies
'''

from pathlib import Path

from ifaxbotcovid import textparser
from ifaxbotcovid import tables
from tests import instruments as inst

class TestUnitParser:

    # sample vars for testing
    sample = 'Тридцать тысяч обезьян'
    sample2 = ' Foo bar  '
    sample_dict = {'Foo' : 'bar', 'Hello' : 'world!'}
    sample_tuple = ('', 'Foo', '')
    sample_tuple2 = ('', 'Foo', '', 'bar')
    sample_tuple3 = ('Foo')
    big_sample = inst.Instruments.get_text_from_file(
        Path('tests/test_data/sample_text.txt')
        )

    parser = textparser.Parser(sample)

    def test_NAcounter(self):
        count = TestUnitParser.parser.NAcounter()
        assert count == 12, "Function doesn't work correctly"

    def test_del_space(self):
        result = TestUnitParser.parser.del_space(TestUnitParser.sample2)
        assert result == 'Foobar'
    
    def test_get_key(self):
        result = TestUnitParser.parser.get_key(TestUnitParser.sample_dict, 'world!')
        assert result == 'Hello'
    
    class TestChooseValue:
        
        def test_choose_value1(self):
            result = TestUnitParser.parser.choose_value(TestUnitParser.sample_tuple)
            assert result == 'Foo'
        
        def test_choose_value2(self):
            result = TestUnitParser.parser.choose_value(TestUnitParser.sample_tuple2)
            assert result == 'Foo'
        
        def test_choose_value3(self):
            result = TestUnitParser.parser.choose_value(TestUnitParser.sample_tuple3)
            assert result == 'Foo'

        def test_choose_value4(self):
            result = TestUnitParser.parser.choose_value(TestUnitParser.sample)
            assert result == TestUnitParser.sample
        # class ends here
    
    class TestComma:

        def test_comma1000(self):
            result = TestUnitParser.parser.comma1000('123456')
            assert result == '123,46'
        
        def test_comma(self):
            result = TestUnitParser.parser.comma('1234.56')
            assert result == '1234,56'

    class TestChangeShape:

        def test_change_shape(self):
            result = TestUnitParser.parser.change_shape('1098007')
            assert result == '1 млн 098 тыс. 007'
        
        def test_change_shape2(self):
            result = TestUnitParser.parser.change_shape('10376')
            assert result == '10 тыс. 376'

        def test_change_shape3(self):
            result = TestUnitParser.parser.change_shape('376')
            assert result == '376'

    class TestTableDetection:

        def test_find_tables(self):
            ready_cases, ready_deaths, tlog = tables.tables(
                TestUnitParser.big_sample, 
                short=100
                )
            condition1 = ready_cases.startswith('По информации оперативного штаба, еще')
            condition2 = ready_deaths.startswith('Согласно данным оперштаба о смертности,')
            condition3 = 'Ошибка' not in tlog
            assert condition1 and condition2 and condition3,\
        f'Failed to detect tables: ready_cases - {condition1}, ready_deaths = {condition2}'
    
    class TestVars:

        def test_vars_finding(self):
            text, log, parser = inst.Instruments.parse(
                TestUnitParser.big_sample, 
                get_parser=True # getting the parser object for analysis
                )
            values = parser.values
            expected_values = {
                'russia_new_cases' : '7920',
                'russia_current_pace' : '+0,16%',
                'russia_new_deaths' : '390',
                'russia_new_recovered' : '9561',
                'russia_total_cases' : '4965676',
                'moscow_new_cases' : '2096',
                'moscow_new_deaths' : '61',
                'moscow_new_recovered' : '2663',
                'russia_total_deaths' : '116965',
                'russia_total_recovered' : '4581787'
                }
            errors = 0
            failed_keys = []
            for key in expected_values.keys():
                if values[key] != expected_values[key]:
                    errors += 1
                    failed_keys.append(key)
            assert errors == 0,\
                f'Expected values did not found. Failed keys: {str(failed_keys)}'