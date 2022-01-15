from tests import instruments as inst
from ifaxbotcovid.config.utils import helpmessage, startmessage


class TestHelpMessage:

    def test_get_helpmessage_init(self):
        message = helpmessage.helpmsg()
        assert message

    def test_helpmessage_tags(self):
        message = helpmessage.helpmsg()
        assert inst.Instruments.check_html_tags(message)


class TestStartMessage:
    def test_get_startmessage_init(self):
        message = startmessage.startmsg()
        assert message

    def test_startmessage_tags(self):
        message = startmessage.startmsg()
        assert inst.Instruments.check_html_tags(message)
