import urllib.request
import ssl
from io import BytesIO
from dataclasses import dataclass
from typing import Optional

from grok3.grok3api_logger import logger


@dataclass
class GeneratedImage:
    cookies: str
    url: str
    _base_url: str = "https://assets.grok.com"

    def download(self) -> Optional[BytesIO]:
        """Метод для загрузки изображения по заданному URL."""
        try:
            if not self.cookies:
                logger.debug("Нет cookies для загрузки изображения.")
                return None
            image_url = self.url
            if not image_url.startswith('/'):
                image_url = '/' + image_url

            full_url = self._base_url + image_url
            logger.debug(f"Полный URL для загрузки изображения: {full_url}")

            headers = {
                "Cookie": self.cookies,
                "User-Agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                               "AppleWebKit/537.36 (KHTML, like Gecko) "
                               "Chrome/132.0.0.0 Safari/537.36"),
                "Accept": "image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8",
                "Accept-Encoding": "gzip, deflate, br",
                "Accept-Language": "ru-RU,ru;q=0.9",
                "Referer": "https://grok.com/"
            }
            logger.debug(f"Заголовки запроса: {headers}")

            req = urllib.request.Request(full_url, headers=headers)

            context = ssl.create_default_context()
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE

            with urllib.request.urlopen(req, context=context) as response:
                logger.debug("Запрос выполнен, получаем данные изображения.")
                image_data = response.read()
                logger.debug("Изображение успешно загружено.")
                return BytesIO(image_data)
        except Exception as e:
            logger.error(f"При загрузке изображения (download): {e}")
            return None

    def save_to(self, path: str) -> None:
        """
        Скачивает изображение и сохраняет его в файл по указанному пути.
        """
        try:
            logger.debug(f"Попытка сохранить изображение в файл: {path}")
            image_data = self.download()
            if image_data is not None:
                with open(path, "wb") as f:
                    f.write(image_data.getbuffer())
                logger.debug(f"Изображение успешно сохранено в: {path}")
            else:
                logger.debug("Изображение не было загружено, сохранение отменено.")
        except Exception as e:
            logger.error(f"В save_to: {e}")
