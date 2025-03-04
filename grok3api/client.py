import time
from typing import Optional

from grok3api.chat_completion import ChatCompletion
from grok3api import driver
from grok3api.grok3api_logger import logger


class GrokClient:
    """
    Клиент для работы с Grok.
    :param use_xvfb: Флаг для использования Xvfb. По умолчанию True. Имеет значения только на linux.
    """

    def __init__(self, use_xvfb: bool = True):
        try:
            self.use_xvfb = use_xvfb
            # self.auto_close_xvfb = auto_close_xvfb
            # self.cookies = cookies or ""
            # if not self.cookies or self.cookies is None:
            #     self.cookies = _cookies_from_file(cookies_file)
            #     if not self.cookies or self.cookies is None:
            #         self.cookies = _fetch_cookies(self.use_xvfb, self.auto_close_xvfb)
            #         _cookies_to_file(self.cookies, cookies_file)
            self.ChatCompletion = ChatCompletion(self.use_xvfb)
            driver.init_driver()
        except Exception as e:
            logger.error(f"В GrokClient.__init__: {e}")
