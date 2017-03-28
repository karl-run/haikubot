import logging

from haikubot import config
from haikubot.bot import Haikubot

VERSION = 'v0.1'

logging.info('Running haikubot ' + VERSION)

if __name__ == "__main__":
    bot = Haikubot(config.API_KEY)
    try:
        bot.run()
    except:
        bot.clean_up()
