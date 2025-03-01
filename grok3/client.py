import logging
from typing import Optional

from grok3.chat_completion import ChatCompletion



logger = logging.getLogger(__name__)



class GrokClient:
    """
    Клиент для работы с Grok API.
    Параметр cookies не является обязательным — если не передан,
    они будут получены через playwright.
    """
    def __init__(self, cookies: Optional[str] = None):
        self.cookies = cookies or ""
        self.ChatCompletion = ChatCompletion(self.cookies)