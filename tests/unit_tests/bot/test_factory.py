from ifaxbotcovid.bot import factory


def test_factory_creation():
    test_token = 'This098is0987token'
    bot = factory.create_bot(test_token)
    assert bot.token == test_token
