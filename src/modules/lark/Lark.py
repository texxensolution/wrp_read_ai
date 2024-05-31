import lark_oapi as lark
import os


class Lark:
    def __init__(self, app_id=None, app_secret=None, debug=False):
        self.APP_ID = os.getenv('APP_ID') or app_id
        self.APP_SECRET = os.getenv('APP_SECRET') or app_secret
        self.client = lark.Client.builder() \
            .app_id(self.APP_ID) \
            .app_secret(self.APP_SECRET) \

        if debug:
            self.client = self.client.log_level(lark.LogLevel.DEBUG)

        self.client = self.client.build()