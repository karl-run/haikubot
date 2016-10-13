import os
from bot.bot import Haikubot

VERSION = 'v0.0.1'

print('Running haikubot', VERSION)

BOT_ID = os.environ.get("HAIKUBOT_ID")
API_KEY = os.environ.get('HAIKUBOT_API_KEY')


if __name__ == "__main__":
    bot = Haikubot(API_KEY, BOT_ID)
    bot.run()
