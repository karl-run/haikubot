from haikubot import config
from haikubot.bot import Haikubot

if __name__ == "__main__":
    bot = Haikubot(config.API_KEY)
    try:
        bot.run()
    except Exception as err:
        bot.clean_up()
        raise err
