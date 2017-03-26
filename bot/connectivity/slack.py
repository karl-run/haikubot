import logging
from datetime import datetime
from slackclient import SlackClient

import config
from bot.utils.color import string_to_color_hex


class Slack:
    def __init__(self, api_key):
        if api_key is None:
            raise ValueError('You must provide an API key for Slack.')
        self.sc = SlackClient(api_key)

    def connect(self):
        return self.sc.rtm_connect()

    def read(self):
        return self.sc.rtm_read()

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

    def post_haiku_model(self, haiku, channel=config.POST_TO_CHANNEL):
        return self.post_haiku(haiku.haiku, haiku.author, haiku.hid, haiku.link, channel)

    def post_haiku(self, haiku, author, haiku_id, stash_link, channel=config.POST_TO_CHANNEL):
        title = 'Haiku #{}'.format(haiku_id)
        color = string_to_color_hex(author)
        haiku_with_title = [{
            'fallback': '{} av {}'.format(title, author),
            'title': 'Haiku #{}'.format(haiku_id),
            'title_link': stash_link,
            'color': color,
            'footer': '- {}'.format(author),
            'text': haiku
        }]
        logging.info('Posting haiku id {} to channel {}.'.format(haiku_id, channel))

        response = self.post_message(haiku_with_title, channel)

        if not response['ok']:
            logging.error('Unable to post haiku, error: {}'.format(response['error']))
        return response['ok']

    def post_snippet(self, snippet_content, channel):
        result = self.sc.api_call(
            'files.upload',
            title='Haiku export {}'.format(str(datetime.today())),
            content=snippet_content,
            channels=channel
        )
        return result['ok']

    def get_username(self, uid):
        return self.sc.server.users.find(uid)

    def get_channel_name(self, cid):
        channel = self.sc.server.channels.find(cid)
        return channel.name if channel is not None else None

    def get_channel_info(self, cid):
        return self.sc.api_call('channels.info', channel=cid)
