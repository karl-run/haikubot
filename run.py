import logging

from bot.bot import Haikubot
import config

VERSION = 'v0.0.1'

logging.info('Running haikubot ' + VERSION)

if __name__ == "__main__":
    bot = Haikubot(config.API_KEY, config.BOT_ID)
    bot.run()
