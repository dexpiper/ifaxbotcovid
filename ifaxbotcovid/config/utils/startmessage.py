from ifaxbotcovid.config.utils.settings import version


def startmsg():
    with open('ifaxbotcovid/config/messagestart.txt', 'r') as file:
        s = file.read()
    return s.format(version=version)
