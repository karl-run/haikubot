import os
from slackclient import SlackClient

BOT_NAME = 'haikubot'

if 'HAIKUBOT_API_KEY' not in os.environ:
    print('ERROR: No API key found')
    exit()

slack_client = SlackClient(os.environ.get('HAIKUBOT_API_KEY'))

if __name__ == "__main__":
    print('Doing API call')
    api_call = slack_client.api_call("users.list")
    if api_call.get('ok'):
        print('Call OK.')
        # retrieve all users so we can find our bot
        users = api_call.get('members')
        for user in users:
            if 'name' in user and user.get('name') == BOT_NAME:
                print("Bot ID for '" + user['name'] + "' is " + user.get('id'))
    else:
        print("could not find bot user with the name " + BOT_NAME)
