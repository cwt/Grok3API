import urllib.request
import ssl
import logging
from io import BytesIO
from dataclasses import dataclass
from typing import Optional

@dataclass
class GeneratedImage:
    cookies: str
    url: str
    base_url: str = "https://assets.grok.com"

    def download(self) -> Optional[BytesIO]:
        """Метод для загрузки изображения по заданному URL."""
        try:
            if not self.cookies:
                return None
            image_url = self.url
            if not image_url.startswith('/'):
                image_url = '/' + image_url

            full_url = self.base_url + image_url

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

            req = urllib.request.Request(full_url, headers=headers)

            context = ssl.create_default_context()
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE

            with urllib.request.urlopen(req, context=context) as response:
                image_data = response.read()
                return BytesIO(image_data)
        except Exception as e:
            logging.error(f"Ошибка при загрузке изображения: {e}")
            raise

    def save_to(self, path: str) -> None:
        """
        Скачивает изображение и сохраняет его в файл по указанному пути.
        """
        image_data = self.download()
        if image_data is not None:
            with open(path, "wb") as f:
                f.write(image_data.getbuffer())