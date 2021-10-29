#
# Contains starting message for bot users, HTML-form
#

def startmsg():
    try:
        with open('messagestart.txt', 'r') as file:
            s = file.read()
    except FileNotFoundError:
        s = 'Welcome to ifaxbotcovid!'
    return s
