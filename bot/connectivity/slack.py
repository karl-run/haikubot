import logging

import hashlib
from slackclient import SlackClient

import config


class Slack:
    def __init__(self, api_key):
        if api_key is None:
            raise ValueError('You must provide an API key for Slack.')
        self.sc = SlackClient(api_key)

    def get_id(self):
        logging.debug('Getting bot ID')
        api_call = self.sc.api_call("users.list")
        if api_call.get('ok'):
            for user in api_call.get('members'):
                if 'name' in user and user.get('name') == config.BOT_NAME:
                    logging.debug("Bot ID for {} is {}".format(user['name'], user.get('id')))
                    return user.get('id')
        else:
            raise ValueError('No bot with name {} found in user list'.format(config.BOT_NAME))

    def post_message(self, message, channel=config.POST_TO_CHANNEL, as_user=True):
        if isinstance(message, list):
            return self.sc.api_call("chat.postMessage", channel=channel, as_user=as_user, attachments=message)

        return self.sc.api_call("chat.postMessage", channel=channel, as_user=as_user, text=message)

    def post_haiku(self, haiku, author, haiku_id, stash_link, channel=config.POST_TO_CHANNEL):
        haiku_to_post = haiku + " - " + author + "\n"
        title = 'Haiku #{}'.format(haiku_id)
        color = '#' + hex(int(hashlib.md5(author.encode('utf-8')).hexdigest(), 16) % 16777215).replace('0x', '').rjust(6, '0')
        haiku_with_title = [{
            'fallback': '{}, {}'.format(title, haiku_to_post),
            'title': 'Haiku #{}'.format(haiku_id),
            'title_link': stash_link,
            'text': haiku_to_post
        }]
        logging.info('Posting haiku id {} to channel {}.'.format(haiku_id, channel))

        response = self.post_message(haiku_with_title, channel)

        if not response['ok']:
            logging.error('Unable to post haiku, error: {}'.format(response['error']))
        return response['ok']

    def connect(self):
        return self.sc.rtm_connect()

    def read(self):
        return self.sc.rtm_read()

    def get_username(self, uid):
        return self.sc.server.users.find(uid)
