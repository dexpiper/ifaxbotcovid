import time
import os
import logging
from collections import deque as deque

# importing flask
from flask import Flask, request
# importing TelegramBotAPI
import telebot

# internal modules
import ifaxbotcovid.textparser as textparser
import ifaxbotcovid.config.startmessage as startmessage
import ifaxbotcovid.config.settings as settings
import ifaxbotcovid.rpn as rpn

#
# CHANGE TO "FALSE" BEFORE DEPLOY
# 
TESTMODE = False

if TESTMODE == False:
    TOKEN = os.environ['TOKEN']
else:
    # token.py for testing purposes with TOKEN var .gitignore'd
    import ifaxbotcovid.config.token as tkn
    TOKEN = tkn.TOKEN

#
# Setting telebot instance
#
bot = telebot.TeleBot(TOKEN)

# Setting flask and define webhook settings
app = Flask(__name__)
URL = os.environ['URL']

#
# Logging settings
#
logger = logging.getLogger('main')
logger.setLevel(logging.DEBUG)
telebot_logger = telebot.logger
telebot_logger.setLevel(logging.DEBUG)

# creating handlers
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
file_handler = logging.FileHandler('logfile.log')
file_handler.setLevel(logging.DEBUG)

# applying format to handlers
formatter = logging.Formatter('%(asctime)s - %(name)s : %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

# adding handlers
logger.addHandler(console_handler)
logger.addHandler(file_handler)
telebot_logger.addHandler(console_handler)
telebot_logger.addHandler(file_handler)

if TESTMODE == True:
    logger.warning('Working in "test mode", using test token')

# setting the queue to store sequential messages
db = deque(maxlen=2)
db.append( (int(time.time()), '', '') )

#
# Bot Functions
#
def gluer(msg, getlog=False):
    '''
    Function concatenates texts sent in 2 sequentional messages
    from single user with less then 1 sec delay (Telegram cuts
    apart long messages automaticly, but we need to process both 
    pieces)

    getlog key (bool) is optional

    - "db" is a collections.deque object, maxlen=2
    - each item in the queue is a tuple: 
        (time.time, 'message text' and 'chat_id')

    '''
    old_time = int(db[0][0])
    new_time = int(db[1][0])
    old_chat_id = db[0][2]
    new_chat_id = db[1][2]

    if (
        new_time - old_time < 1) and (
        old_chat_id == new_chat_id
        ):

        text = db[0][1] + msg.text # text - склеенный кусок текста
        logger.debug('Long message glued / Склеено длинное сообщение')
        if text[:2].lower() == 'йй' or text[-2:].lower() == 'йй':
            getlog = True
        return text, getlog
    else:
        return None, None

def log_construct(log):
    '''
    Here we construct a single string to send to the user
    as a log message (parsing results)
    '''
    result = ''
    try:
        for el in log:
            if type(el) == list:
                for item in el:
                    result += (item + '\n')
            else:
                result += (el + '\n')
    except Exception as exc:
        logger.warning('Exception raised during log construction: %s' % exc)
    return result

def pre_call(msg):
    '''
    Pre-processing the text from message
    '''
    rawtext = msg.text
    user = msg.from_user.username

    # Firstly, checking if there is the key word with a log request
    # (short procedure)
    if (rawtext[:2].lower() == 'йй' or
        rawtext[-2:].lower() == 'йй'
        ) and ('роспотребнадзор' in rawtext.lower()):

        RPN_constructor = rpn.RPN(rawtext)
        text, log = RPN_constructor.construct(), RPN_constructor.log
        log = log_construct(log)
        bot.send_message(msg.chat.id, text)
        bot.send_message(msg.chat.id, log, parse_mode='HTML')
        logger.info('RPN message sent to %s along with a log' % user)
        return False

    # Secondly, checking the key word without a log request
    # (short procedure)
    elif rawtext[:15].lower() == 'роспотребнадзор':
        RPN_constructor = rpn.RPN(rawtext)
        text = RPN_constructor.construct()
        bot.send_message(msg.chat.id, text)
        logger.info('RPN message sent to %s' % user)
        return False

    # else, bot would process message further    
    else:
        return True

def main_call(msg, text=None):
    '''
    Processing long text 
    '''
    text, getlog = gluer(msg) # sticking together 2 sequentional messages
    user = msg.from_user.username
    
    # checking if there are some other key words in text
    # to process it as a big press-release (long procedure)
    if text != None and all(
        (True if word in text.lower() else False
        for word in settings.key_words)
        ):
        logger.debug('Main_call() reached requesed condition')
        
        try:
            # here we calling long procedure module...
            #
            news_parser = textparser.Parser(text)
            ready_news = news_parser()

            # ...and sending template with the found vars to the user
            #
            if type(ready_news) is tuple: 
                # ready_news came along with a warning message
                bot.send_message(msg.chat.id, ready_news[1])
                bot.send_message(msg.chat.id, ready_news[0])
                logger.info('Ready news text sent to user %s. \
Attention message included: %s' % (
                        user, 
                        ready_news[0][16:-56]) # deleting unnecessery parts of message
                        )
            else:
                # ready_news just came along
                bot.send_message(msg.chat.id, ready_news)
                logger.info('Ready news text sent to user %s' % user)
        except Exception as exc:
            logger.error("An exception raised when processing %s's input: %s" % (user, exc))

    else:
        # nothing to do, returning
        return

    # if user asked for a log, we kindly send it by track...
    #
    if getlog == True: 
        
        log = log_construct(news_parser.log)
        bot.send_message(msg.chat.id, log, parse_mode='HTML')
        logger.info('Log message sent to user %s' % user)

    # ...and, finally, returning back    
    return

def send_log(msg):
    '''
    Sending log to the user
    '''
    try:
        bot.send_document(msg.chat.id, open('logfile.log'), 'document')
    except Exception as exc:
        logger.error('No system log file found! Exception: %s' % exc)
    
#
# Message handlers
#
@bot.message_handler(commands=['start'])
def answer_start(message):
    '''
    Bot sends welcome message
    '''
    bot.send_message(message.chat.id, startmessage.s, parse_mode='HTML')
    logger.info('User %s issued "start" command' % message.from_user.username)
    user = message.from_user.username
    chat_id = message.chat.id
    if (user, chat_id) not in settings.users:
        settings.users.append((user, chat_id))

@bot.message_handler(commands=['syslog'])
def syslog_sender(message):
    '''
    Bot sends system log as a file (admin only)
    '''
    user = message.from_user.username
    chat_id = message.chat.id
    logger.info('User %s requested "syslog" file via command' % user)
    if chat_id in settings.admins:
        logger.debug('Admin privileges grunted')
        send_log(message)
    else:
        logger.warning('Access to user %s denied' % user)
        bot.send_message(message.chat.id, '<b>Access denied</b>', parse_mode='HTML')

@bot.message_handler(commands=['users'])
def users_sender(message):
    '''
    Bot sends list of users (admin only)
    '''
    user = message.from_user.username
    chat_id = message.chat.id
    logger.info('User %s issued "users" command' % user)
    if chat_id in settings.admins:
        logger.debug('Admin privileges grunted')
        if settings.users:
            user_list = '<b>Registered users:</b>\n\n'
            counter = 0
            for item in settings.users:
                counter += 1
                _name = item[0]
                _id = item[1]
                user_list += f'{counter}. Name: {_name}, chat_id: {_id}\n'
            user_list += f'\n<b>Total: {counter}</b>'
            logger.debug(f'USER LIST: {user_list}')
            bot.send_message(message.chat.id, user_list, parse_mode='HTML')
        else:
            bot.send_message(message.chat.id, 'No users registered')
    else:
        logger.warning('Access to user %s denied' % user)
        bot.send_message(message.chat.id, '<b>Access denied</b>', parse_mode='HTML')
    
@bot.message_handler(content_types=['text'])
def base_function(message):
    '''
    Bot process any text sent to it.
    1) Short text with "Роспотребнадзор" in it whould be dealed 
    as an RPN message. A short string without the key word would
    yeild no answer.
    2) Else, any long text in two messages sent one by one with
    a very short interval would be glued together and parsed as
    a COVID-19 press-reliase. User will recieve a template answer
    with found variables inserted in gaps. 
    3) If no values found, user will get empty template with gaps
    and a warning message.
    '''
    logger.debug('User %s sent some text' % message.from_user.username)
    db.append((int(message.date), message.text, message.chat.id))
    proceed_mode = pre_call(message)
    user = message.from_user.username
    chat_id = message.chat.id
    if (user, chat_id) not in settings.users:
        settings.users.append((user, chat_id))        
    if proceed_mode == False:
        logger.debug('proceed_mode == False, returned')
        return
    else:
        main_call(message)
        return

#
# Routes
#
@app.route('/' + TOKEN, methods=['POST'])
def getMessage():
    bot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])
    return "!", 200

@app.route('/setwebhook', methods=['GET', 'POST'])
def set_webhook():
    bot.remove_webhook()
    s = bot.set_webhook('{URL}{HOOK}'.format(URL=URL, HOOK=TOKEN))
    if s:
        return "webhook setup ok"
    else:
        return "webhook setup failed"

@app.route('/')
def index():
    return '.'


if __name__ == '__main__':
    # starting server
    app.run(threaded=True)
