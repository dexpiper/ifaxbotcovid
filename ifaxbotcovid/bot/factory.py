import logging

from flask import Flask
import telebot

from ifaxbotcovid.bot.logic import CovidChef


def create_bot(tkn, get_logger=False, loglevel=logging.INFO):
    '''
    Usage:
    bot, logger = create_bot(TOKEN, get_logger=True)
        or
    bot = create_bot(TOKEN)
    '''
    bot = telebot.TeleBot(tkn, parse_mode=None)
    if get_logger:
        logger = telebot.logger
        telebot.logger.setLevel(loglevel)
        return bot, logger
    return bot


def create_chef(**kwargs):
    chef = CovidChef(**kwargs)
    return chef


def create_app():
    return Flask(__name__)
