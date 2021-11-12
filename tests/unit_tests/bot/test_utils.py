from pytest import fixture
from unittest.mock import Mock

from ifaxbotcovid.bot.utils import CommandParser


class TestCommandParser:

    @fixture
    def sample_text(self):
        text = ' '.join((
            'This is a long text.\n',
            'We gotta test it, finding some user commands',
            'some good user put inside.'
        ))
        return text

    def test_command_list_creation(self):
        asfile = True
        logrequest = True
        short = 125

        r = CommandParser.CommandList(asfile=asfile, logrequest=logrequest,
                                      short=short)
        assert r.asfile
        assert r.logrequest
        assert r.short == 125

    def test_get_short_accurate(self):
        expected = 125
        string = ' '.join((
            'This is some\tlong string.',
            'Very, very long foobar looking out.\n',
            f'And a $${expected} (inside).'
        ))
        r = CommandParser._get_short(string)
        assert r == expected

    def test_get_short_bad(self):
        string = ' '.join((
            'This other \tlong string.\n',
            'And a $$foo1 (inside).'
        ))
        r = CommandParser._get_short(string)
        assert r == 0

    def test_get_short_bad2(self):
        string = 'foobar123$'
        r = CommandParser._get_short(string)
        assert r == 0

    def test_get_short_bad3(self):
        string = ''
        r = CommandParser._get_short(string)
        assert r == 0

    def test_get_settings_all(self, sample_text):
        text = ''.join((
            sample_text,
            '$$250йй'
        ))
        message = Mock()
        message.text = text
        assert message.text
        settings = CommandParser.get_settings(message)
        assert settings.asfile
        assert settings.short == 250
        assert settings.logrequest

    def test_get_settings_only_log(self, sample_text):
        text = ''.join((
            sample_text,
            'йй'
        ))
        message = Mock()
        message.text = text
        assert message.text
        settings = CommandParser.get_settings(message)
        assert not settings.asfile
        assert not settings.short
        assert settings.logrequest

    def test_get_settings_only_file(self, sample_text):
        text = ''.join((
            sample_text,
            '$$'
        ))
        message = Mock()
        message.text = text
        assert message.text
        settings = CommandParser.get_settings(message)
        assert settings.asfile
        assert not settings.short
        assert not settings.logrequest
