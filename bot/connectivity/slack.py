from slackclient import SlackClient


class Slack:
    def __init__(self, api_key):
        self.sc = SlackClient(api_key)

    def post_message(self, message, channel='haikubot-test', as_user=True):
        return self.sc.api_call("chat.postMessage", channel=channel, text=message, as_user=as_user)

    def post_haiku(self, haiku, author, channel='haikubot-test'):
        haiku_to_post = haiku + " - " + author + "\n"
        response = self.post_message(haiku_to_post, channel)
        # TODO actually check for success
        success = response is not None
        return success

    def connect(self):
        return self.sc.rtm_connect()

    def read(self):
        return self.sc.rtm_read()

    def get_username(self, uid):
        return self.sc.server.users.find(uid)
