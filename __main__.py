import telebot
import time
import os
from collections import deque as deque
import threading

import parser
import startmessage
import rpn

TOKEN = os.environ['TOKEN']
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

def rpn_call(msg):
    rawtext = msg.text
    if rawtext[:2].lower() == 'йй' or rawtext[-2:].lower() == 'йй' and 'Роспотребнадзор:' in rawtext:
        text, log = rpn.call(rawtext)
        log = log_construct(log)
        bot.send_message(msg.chat.id, text)
        bot.send_message(msg.chat.id, log, parse_mode='HTML')
        return False
    elif rawtext[:16].lower() == 'роспотребнадзор:':
        text, log = rpn.call(rawtext)
        bot.send_message(msg.chat.id, text)
        return False
    else:
        return True

def main_call(msg, text=None):
    text, getlog = gluer(msg)
    if text != None:
        news_parser = parser.Parser(text)
        ready_news = news_parser()
        bot.send_message(msg.chat.id, ready_news)
    if getlog == True:
        log = log_construct(news_parser.log)
        bot.send_message(msg.chat.id, log, parse_mode='HTML')
    return
            

@bot.message_handler(commands=['start'])
def answer_start(message):
    bot.send_message(message.chat.id, startmessage.s, parse_mode='HTML')

@bot.message_handler(content_types=['text'])
def base_function(message):
    db.append((int(message.date), message.text))
    proceed_mode = rpn_call(message)
    if proceed_mode == False:
        return
    else:
        main_call(message)
        return
        

if __name__ == '__main__':
    print('Starting botcovid...')
    db = deque(maxlen=2); db.append( (int(time.time()), '') )
    bot.polling(none_stop=True)

