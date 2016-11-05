import logging
import os

"""
The REST-URL is:
http://stash.ex.com/rest/api/1.0/projects/KEY/repos/REPO_NAME/pull-requests

For multiple repositories provide a single key and multiple repo names.

For multpile repositories over multiple projects add more entries to the STASH_REPOSITORIES
list as needed.

BOT_ID is used to identify bot in commands.
"""

# User provided details
API_KEY = os.environ.get('HAIKUBOT_API_KEY')
BOT_NAME = 'haikubot'
POST_TO_CHANNEL = 'haikubot-test'
STASH_URL = 'http://stash.example.com'
STASH_HEADERS = None
SSL_VERIFY = None
STASH_REPOSITORIES = [
    {
        'REPO_KEY': 'KEY',
        'REPOSITORIES': ['REPO_NAME_1', 'REPO_NAME_2']
    }
]
STASH_POLL_TIME = 2  # Seconds
# TODO add auth

# Database
DATABASE_PATH = './'

# Debugging
DEBUG = True
DEBUG_URL = 'bot/connectivity/example_stash.json'

# Logging
LOG_PATH = ''  # Empty for console output
LOG_LEVEL = logging.DEBUG  # debug, info, warning, error, critical

logging.basicConfig(
    level=LOG_LEVEL,
    filename=LOG_PATH,
    format='%(asctime)s %(name)s %(levelname)s: %(message)s'
)
