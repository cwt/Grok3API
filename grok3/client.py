import time
from typing import Optional

from grok3.chat_completion import ChatCompletion, _cookies_from_file, _fetch_cookies
from grok3.grok3api_logger import logger


class GrokClient:
    """
    Клиент для работы с Grok API.

    :param cookies: Строка с cookie, если передана, она будет использованы для авторизации.
                    Если не переданы, будут получены через Chrome.
    :param use_xvfb: Флаг для использования Xvfb. По умолчанию True. Имеет значения только на linux.
    :param auto_close_xvfb: Флаг для автоматического закрытия Xvfb после использования. По умолчанию False. Имеет значения только на linux.
    :param cookies_file: Путь к файлу, из которого будут загружаться куки, если они не переданы.
                     По умолчанию "cookies.txt".
    """

    def __init__(self,
                 cookies: Optional[str] = None,
                 use_xvfb: bool = True,
                 auto_close_xvfb: bool = False,
                 cookies_file: Optional[str] = "cookies.txt"):
        try:
            self.use_xvfb = use_xvfb
            self.auto_close_xvfb = auto_close_xvfb
            self.cookies = cookies or ""
            if not self.cookies or self.cookies is None:
                self.cookies = _cookies_from_file(cookies_file)
                if not self.cookies or self.cookies is None:
                    self.cookies = _fetch_cookies(self.use_xvfb, self.auto_close_xvfb)
            self.ChatCompletion = ChatCompletion(self.cookies, self.use_xvfb, self.auto_close_xvfb)
        except Exception as e:
            logger.error(f"В GrokClient.__init__: {e}")

    def farm_cookies(self,
                     file_path: Optional[str] = "cookies.txt",
                     count: Optional[int] = None,
                     timeout: Optional[int] = None):
        """
        Циклично получает куки с использованием _fetch_cookies и дописывает их в указанный файл.

        :param file_path: Путь к файлу для сохранения куки. По умолчанию "cookies.txt".
        :param count: Количество куки, после достижения которого метод остановится.
                      Если None, ограничений по количеству нет.
        :param timeout: Таймаут в секундах, по истечении которого метод остановится, закончив итерацию.
                        Если None, ограничений по времени нет.
        """
        start_time = time.time()
        cookie_counter = 0

        while (count is None or cookie_counter < count) and (timeout is None or (time.time() - start_time) < timeout):
            cookie = _fetch_cookies(self.use_xvfb, self.auto_close_xvfb)
            with open(file_path, "a", encoding="utf-8") as f:
                f.write(cookie.strip() + "\n")
                logger.debug(f"farm_cookies: {cookie_counter+1}: {cookie}")
            cookie_counter += 1

        logger.debug(f"farm_cookies: получено {cookie_counter} записей в {file_path}")
