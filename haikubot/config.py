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

# Basic details always required
API_KEY = os.environ.get('HAIKUBOT_API_KEY')
BOT_NAME = 'haikubot'
POST_TO_CHANNEL = 'haikubot-test'
SUPER_MOD = 'karlos'
STASH_URL = 'http://stash.example.com'
STASH_HEADERS = None
SSL_VERIFY = None
STASH_REPOSITORIES = [
    {
        'REPO_KEY': 'KEY',
        'REPOSITORIES': ['REPO_NAME_1', 'REPO_NAME_2']
    }
]
STASH_POLL_TIME = 60  # Seconds
READ_WEBSOCKET_DELAY = 1  # Seconds, used for Slack communication
GROUP_HAIKU_EXPORT_SIZE = 100 # How many haikus to limit into a single 'file' export

# Database
FILE_DB = True
DATABASE_PATH = './'

# If FILE_DB is set to false, also provide:
DB_ADAPTER = 'postgresql'
DB_URL = 'example.com:5432/haikubot'
DB_USER = 'haikubot'
DB_PW = os.environ.get('HAIKUBOT_DB_PW')

# Debugging
DEBUG = True
DEBUG_URL = 'data/example_stash.json'

# Logging
LOG_PATH = ''  # Empty for console output
LOG_LEVEL = logging.DEBUG  # debug, info, warning, error, critical

logging.basicConfig(
    level=LOG_LEVEL,
    filename=LOG_PATH,
    format='%(asctime)s %(name)s %(levelname)s: %(message)s'
)
