#!/usr/bin/env python
# -*- coding: utf-8 -*-

import ConfigParser
import logging
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

def start(bot, update):
	update.message.reply_text('Hi!');

def help(bot, update):
	update.message.reply_text('Help!');

def avatar(bot, update):
	f = open("data/1.png");
	update.message.reply_photo(f);
	f.close();

def echo(bot, update):
	pass;

def error(bot, update, error):
	logger.warn('Update "%s" caused error "%s"' % (update, error));

def main():
	cf = ConfigParser.ConfigParser();
	cf.read("pab.conf");
	token = cf.get("bot", "bot_token");
	print token
    
	updater = Updater(token);
	dp = updater.dispatcher;
	
	dp.add_handler(CommandHandler("start", start));
	dp.add_handler(CommandHandler("help", help));
	dp.add_handler(CommandHandler("avatar", avatar));
	dp.add_handler(MessageHandler(Filters.text, echo));
	dp.add_error_handler(error);
	
	updater.start_polling();
	updater.idle();

if __name__ == '__main__':
	main();
