import gzip
import json
import logging
import os
import urllib.request
import time
from typing import Any
import urllib.error

from grok3.types.GrokResponse import GrokResponse

try:
    import undetected_chromedriver as uc
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.common.by import By
except ImportError:
    uc = None


logger = logging.getLogger(__name__)
TIMEOUT = 30


def _fetch_cookies() -> str:
    """Получение cookies через undetected_chromedriver с обходом Cloudflare."""
    logger.info("Пробуем получить новые куки...")
    if uc is None:
        logger.error(
            "undetected_chromedriver не установлен, не удается обновить куки. Попробуйте: pip install undetected_chromedriver")
        return ""

    uc.Chrome.__del__ = lambda self_obj: None

    logger.debug("Запуск браузера...")
    options = uc.ChromeOptions()
    options.add_argument("--no-sandbox")
    options.add_argument("--incognito")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-dev-shm-usage")

    driver = uc.Chrome(options=options, headless=False, use_subprocess=False)
    driver.minimize_window()

    try:
        logger.debug("Переход на https://grok.com/")
        driver.get("https://grok.com/")

        logger.debug("Ожидаем появления поля ввода...")
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.relative.z-10 textarea"))
        )
        logger.debug("Поле ввода обнаружено, ждём ещё 2 секунды...")
        time.sleep(2)

        cookies = driver.get_cookies()
        if not cookies:
            logger.warning("Куки не найдены, пробуем ещё раз через 3 секунды...")
            time.sleep(1)
            cookies = driver.get_cookies()

        cookie_string = "; ".join([f"{cookie['name']}={cookie['value']}" for cookie in cookies])
        logger.debug(f"Полученные куки: {cookie_string}")
        return cookie_string

    except Exception as e:
        logger.error(f"Ошибка при получении куки: {str(e)}")
        return ""

    finally:
        if driver:
            try:
                logger.debug("Закрытие браузера")
                driver.quit()
            except Exception as e:
                logger.debug(f"Ошибка при закрытии браузера: {e}")

def _save_cookies_to_env(cookie_string, env_file=".env"):
    """Сохраняет строку cookies в .env файл без использования dotenv."""
    if not cookie_string or not env_file or cookie_string is None:
        return

    if " " in cookie_string or "=" in cookie_string or ";" in cookie_string:
        cookie_string = f'"{cookie_string}"'

    lines = []
    if os.path.exists(env_file):
        with open(env_file, "r", encoding="utf-8") as file:
            lines = file.readlines()

    with open(env_file, "w", encoding="utf-8") as file:
        found = False
        for line in lines:
            if line.startswith("INCOGNITO_COOKIES="):
                file.write(f"INCOGNITO_COOKIES={cookie_string}\n")
                found = True
            else:
                file.write(line)
        if not found:
            file.write(f"INCOGNITO_COOKIES={cookie_string}\n")

    logger.debug(f"INCOGNITO_COOKIES сохранены в {env_file}")

def _get_cookies_from_env(env_file=".env") -> str:
    """
    Извлекает значение переменной INCOGNITO_COOKIES из .env файла.

    Если переменная найдена, возвращает её значение без окружающих кавычек,
    иначе возвращает пустую строку.
    """
    if not os.path.exists(env_file):
        logger.debug(f"Файл {env_file} не найден.")
        return ""

    with open(env_file, "r", encoding="utf-8") as file:
        lines = file.readlines()

    for line in lines:
        if line.startswith("INCOGNITO_COOKIES="):
            cookie_value = line[len("INCOGNITO_COOKIES="):].strip()
            if (cookie_value.startswith('"') and cookie_value.endswith('"')) or \
                    (cookie_value.startswith("'") and cookie_value.endswith("'")):
                cookie_value = cookie_value[1:-1]
            logger.debug("INCOGNITO_COOKIES успешно извлечены из .env файла.")
            return cookie_value

    logger.debug("INCOGNITO_COOKIES не найдены в .env файле.")
    return ""



class ChatCompletion:
    BASE_URL = "https://grok.com/rest/app-chat/conversations/new"
    TIMEOUT = TIMEOUT

    def __init__(self, cookies: str = ""):
        self.cookies = cookies

    def _send_request(self, payload, headers, base_url, auto_update_cookies):
        """Синхронный HTTP-запрос через urllib.request"""
        timeout = TIMEOUT
        try:
            req = urllib.request.Request(
                url=base_url,
                data=json.dumps(payload).encode("utf-8"),
                headers=headers,
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=timeout) as response:
                raw_data = response.read()
                if response.info().get("Content-Encoding") == "gzip":
                    raw_data = gzip.decompress(raw_data)
                text = raw_data.decode("utf-8")

                final_dict = {}
                for line in text.splitlines():
                    try:
                        parsed = json.loads(line)
                        if "modelResponse" in parsed["result"]["response"]:
                            final_dict = parsed
                            break
                    except (json.JSONDecodeError, KeyError):
                        continue
                return final_dict
        except urllib.error.HTTPError as e:
            if "Too Many Requests" in str(e) or "Unauthorized":
                logger.info("Ошибка HTTP-запроса: Too Many Requests (HTTP Error 429).")
                if auto_update_cookies:
                    logger.info("Пробуем обновить Cookies...")
                    self.cookies = _fetch_cookies()
                    if self.cookies and self.cookies != "" and not self.cookies is None:
                        logger.info("Успешно! Пробуем повторить запрос...")
                        headers["Cookie"] = self.cookies
                        return self._send_request(payload, headers, base_url, False)
            else:
                logger.error(f"Ошибка HTTP-запроса: {str(e)}")
            return {}
        except Exception as e:
            logger.error(f"Ошибка HTTP-запроса: {str(e)}")
            return {}

    def create(self, message: str, **kwargs: Any) -> GrokResponse:
        """
        Отправляет запрос к API Grok с одним сообщением и дополнительными параметрами.

        Args:
            message (str): Сообщение пользователя для отправки в API.
            **kwargs: Дополнительные параметры для настройки запроса.

        Keyword Args:
            auto_update_cookies (bool): Обновлять ли cookies автоматически при необходимости. По умолчанию True.
            env_file (str): Путь к файлу окружения для сохранения cookies. По умолчанию ".env".
            temporary (bool): Указывает, является ли сессия или запрос временным. По умолчанию False.
            modelName (str): Название модели AI для обработки запроса. По умолчанию "grok-3".
            fileAttachments (List[Dict[str, str]]): Список вложений файлов. Каждое вложение — словарь с ключами "name" и "content".
            imageAttachments (List[Dict[str, str]]): Список вложений изображений. Аналогично fileAttachments.
            customInstructions (str): Дополнительные инструкции или контекст для модели. По умолчанию пустая строка.
            deepsearch preset (str): Пред установка для глубокого поиска. По умолчанию пустая строка. Передаётся через словарь.
            disableSearch (bool): Отключить функцию поиска модели. По умолчанию False.
            enableImageGeneration (bool): Включить генерацию изображений в ответе. По умолчанию True.
            enableImageStreaming (bool): Включить потоковую передачу изображений. По умолчанию True.
            enableSideBySide (bool): Включить отображение информации бок о бок. По умолчанию True.
            imageGenerationCount (int): Количество генерируемых изображений. По умолчанию 2.
            isPreset (bool): Указывает, является ли сообщение предустановленным. По умолчанию False. Передаётся через словарь.
            isReasoning (bool): Включить режим рассуждений в ответе модели. По умолчанию False. Передаётся через словарь.
            returnImageBytes (bool): Возвращать данные изображений в виде байтов. По умолчанию False.
            returnRawGrokInXaiRequest (bool): Возвращать необработанный вывод модели. По умолчанию False.
            sendFinalMetadata (bool): Отправлять финальные метаданные с запросом. По умолчанию True.
            toolOverrides (Dict[str, Any]): Словарь для переопределения настроек инструментов. По умолчанию пустой словарь.

        Returns:
            GrokResponse: Объект ответа от API Grok.
        """
        base_headers = {
            "Content-Type": "application/json",
            "User-Agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                           "(KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36"),
            "Accept": "*/*",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "ru-RU,ru;q=0.9",
            "Origin": "https://grok.com",
            "Referer": "https://grok.com/",
        }

        headers = base_headers.copy()

        auto_update_cookies = kwargs.get("auto_update_cookies", True)
        env_file = kwargs.get("env_file", ".env")

        payload = {
            "temporary": False,
            "modelName": "grok-3",
            "message": message,
            "fileAttachments": [],
            "imageAttachments": [],
            "customInstructions": "",
            "deepsearch preset": "",
            "disableSearch": False,
            "enableImageGeneration": True,
            "enableImageStreaming": True,
            "enableSideBySide": True,
            "imageGenerationCount": 2,
            "isPreset": False,
            "isReasoning": False,
            "returnImageBytes": False,
            "returnRawGrokInXaiRequest": False,
            "sendFinalMetadata": True,
            "toolOverrides": {}
        }

        filtered_kwargs = {k: v for k, v in kwargs.items() if k not in ("auto_update_cookie", "env_file", message)}
        payload.update(filtered_kwargs)

        if not self.cookies or self.cookies is None:
            self.cookies = _get_cookies_from_env(env_file)
            if not self.cookies or self.cookies is None:
                self.cookies = _fetch_cookies()

        headers["Cookie"] = self.cookies

        logger.debug(f"Grok payload: {payload}")

        response_json = self._send_request(payload, headers, self.BASE_URL, auto_update_cookies)

        if isinstance(response_json, dict):
            _save_cookies_to_env(self.cookies, env_file)
            return GrokResponse(response_json, self.cookies)

        logger.error("Ошибка: неожиданный формат ответа от сервера")
        return GrokResponse(response_json, self.cookies)