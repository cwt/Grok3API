from typing import Optional

from grok3.chat_completion import ChatCompletion, _get_cookies_from_env, _fetch_cookies
from grok3.grok3api_logger import logger


class GrokClient:
    """
    Клиент для работы с Grok API.

    :param cookies: Строка с cookie, если передана, она будет использованы для авторизации.
                    Если не переданы, будут получены через Chrome.
    :param use_xvfb: Флаг для использования Xvfb. По умолчанию True. Имеет значения только на linux.
    :param auto_close_xvfb: Флаг для автоматического закрытия Xvfb после использования. По умолчанию False. Имеет значения только на linux.
    :param env_file: Путь к файлу .env, из которого будут загружаться куки, если они не переданы.
                     По умолчанию ".env".
    """

    def __init__(self,
                 cookies: Optional[str] = None,
                 use_xvfb: bool = True,
                 auto_close_xvfb: bool = False,
                 env_file: Optional[str] = ".env"):
        try:
            self.use_xvfb = use_xvfb
            self.auto_close_xvfb = auto_close_xvfb
            self.cookies = cookies or ""
            if not self.cookies or self.cookies is None:
                self.cookies = _get_cookies_from_env(env_file)
                if not self.cookies or self.cookies is None:
                    self.cookies = _fetch_cookies(self.use_xvfb, self.auto_close_xvfb)
            self.ChatCompletion = ChatCompletion(self.cookies, self.use_xvfb, self.auto_close_xvfb)
        except Exception as e:
            logger.error(f"В GrokClient.__init__: {e}")
