import telebot
import time
from collections import deque as deque
import threading

import parser
import startmessage

TOKEN = '1381452795:AAEBHE7eDd14KKrNLzku1E5nJnO0TllWR3Q'
bot = telebot.TeleBot(TOKEN)

def gluer(msg, getlog=False):
    old_time = int(db[0][0])
    new_time = int(db[1][0])
    '''if msg.text[:2].lower() == 'йй':
        return None, None'''
    if new_time - old_time < 1:
        text = db[0][1] + msg.text # text - склеенный кусок текста
        print('Склеено длинное сообщение')
        if text[:2].lower() == 'йй' or text[-2:].lower() == 'йй':
            getlog = True
        return text, getlog
    else:
        return None, None

def log_construct(log):
    result = ''
    try:
        for el in log:
            if type(el) == list:
                for item in el:
                    result += (item + '\n')
            else:
                result += (el + '\n')
    except Exception as exc:
        print(exc)
    return result

@bot.message_handler(commands=['start'])
def answer_start(message):
    bot.send_message(message.chat.id, startmessage.s, parse_mode='HTML')

@bot.message_handler(content_types=['text'])
def base_function(message):
    db.append((int(message.date), message.text))
    text, getlog = gluer(message)
    if text != None:
        news_parser = parser.Parser(text)
        ready_news = news_parser()
        bot.send_message(message.chat.id, ready_news)
    if getlog == True:
        log = log_construct(news_parser.log)
        bot.send_message(message.chat.id, log, parse_mode='HTML')
        

if __name__ == '__main__':
    db = deque(maxlen=2); db.append( (int(time.time()), '') )
    bot.polling(none_stop=True)
