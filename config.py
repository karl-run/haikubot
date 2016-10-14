import os

"""
The REST-URL is:
http://stash.ex.com/rest/api/1.0/projects/KEY/repos/REPO_NAME/pull-requests

For multiple repositories provide a single key and multiple repo names.

For multpile repositories over multiple projects add more entries to the STASH_REPOSITORIES
list as needed.

BOT_ID is used to identify bot in commands.
"""

API_KEY = os.environ.get('HAIKUBOT_API_KEY')
BOT_ID = os.environ.get('HAIKUBOT_ID')
STASH_URL = 'http://stash.example.com'
STASH_REPOSITORIES = [
    {
        'REPO_KEY': 'KEY',
        'REPOSITORIES': ['REPO_NAME_1', 'REPO_NAME_2']
    }
]
STASH_POLL_TIME = 2  # Seconds
# TODO add auth

DEBUG = False
DEBUG_URL = 'bot/connectivity/example_stash.json'
