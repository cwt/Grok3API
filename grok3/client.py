from typing import Optional

from grok3.chat_completion import ChatCompletion, _get_cookies_from_env, _fetch_cookies
from grok3.grok3api_logger import logger


class GrokClient:
    """
    Клиент для работы с Grok API.
    Параметр cookies не является обязательным — если не передан,
    они будут получены через playwright.
    """
    def __init__(self, cookies: Optional[str] = None, env_file: Optional[str] = ".env"):
        try:
            self.cookies = cookies or ""
            if not self.cookies or self.cookies is None:
                self.cookies = _get_cookies_from_env(env_file)
                if not self.cookies or self.cookies is None:
                    self.cookies = _fetch_cookies()
            self.ChatCompletion = ChatCompletion(self.cookies)
        except Exception as e:
            logger.error(f"В GrokClient.__init__: {e}")