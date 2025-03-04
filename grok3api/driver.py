import time
from typing import Optional
import os
import shutil
import subprocess
import sys

from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.webdriver import WebDriver as ChromeWebDriver
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec

from grok3api.grok3api_logger import logger

DRIVER: Optional[ChromeWebDriver] = None
TIMEOUT = 45
USE_XVFB = True
BASE_URL = "https://grok.com/"


def init_driver(wait_loading: bool = True, use_xvfb: bool = True):
    """Запускает ChromeDriver и проверяет/устанавливает базовый URL."""
    try:
        global DRIVER, USE_XVFB
        USE_XVFB = use_xvfb
        if USE_XVFB: safe_start_xvfb()

        if DRIVER:
            minimize()
            current_url = DRIVER.current_url
            if current_url != BASE_URL:
                logger.debug(f"Текущий URL ({current_url}) не совпадает с базовым ({BASE_URL}), переходим...")
                DRIVER.get(BASE_URL)
                if wait_loading:
                    logger.debug("Ждём появления поля ввода после перехода...")
                    WebDriverWait(DRIVER, 30).until(
                        ec.presence_of_element_located((By.CSS_SELECTOR, "div.relative.z-10 textarea"))
                    )
                    logger.debug("Поле ввода найдено, ждём ещё 2 секунды...")
                    time.sleep(2)
            return
        uc.Chrome.__del__ = lambda self_obj: None

        options = Options()
        options.add_argument("--no-sandbox")
        options.add_argument("--incognito")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-dev-shm-usage")

        DRIVER = uc.Chrome(options=options, headless=False, use_subprocess=False)
        minimize()
        DRIVER.get(BASE_URL)
        if wait_loading:
            logger.debug("Ждём появления поля ввода...")
            WebDriverWait(DRIVER, 30).until(
                ec.presence_of_element_located((By.CSS_SELECTOR, "div.relative.z-10 textarea"))
            )
            logger.debug("Поле ввода найдено, ждём ещё 2 секунды...")
            time.sleep(2)
        logger.debug("Браузер запущен.")

    except Exception as e:
        logger.error(f"Не удалось запустить браузер: {e}")
        raise

def safe_start_xvfb():
    """Запускает Xvfb, если он ещё не запущен, для работы Chrome без GUI на Linux."""
    if sys.platform.startswith("linux"):
        if shutil.which("google-chrome") is None and shutil.which("chrome") is None:
            logger.error("В _fetch_cookies: Chrome не установлен, не удается обновить куки. Установите Chrome.")
            return
        if shutil.which("Xvfb") is None:
            logger.warning("⚠ Xvfb не установлен! Он нужен при отсутствии GUI на вашем линукс. Установите его командой: sudo apt install xvfb")
            return

        result = subprocess.run(["pgrep", "-f", f"Xvfb :99"], capture_output=True, text=True)

        if not result.stdout.strip():
            logger.debug("Запускаем Xvfb...")
            os.system("Xvfb :99 -screen 0 800x600x8 >/dev/null 2>&1 &")

            for _ in range(5):
                time.sleep(2)
                result = subprocess.run(["pgrep", "-f", f"Xvfb :99"], capture_output=True, text=True)
                if result.stdout.strip():
                    logger.debug("В _start_xvfb_if_needed: Xvfb успешно запущен.")
                    os.environ["DISPLAY"] = ":99"
                    return
            logger.error("В _start_xvfb_if_needed: Xvfb не запустился! Проверьте установку.")
            os.environ["DISPLAY"] = ":99"
        else:
            logger.debug("В _start_xvfb_if_needed: Xvfb уже запущен.")
            os.environ["DISPLAY"] = ":99"


def restart_session():
    """Перезапускаем сессию, очищая куки, localStorage, sessionStorage и перезагружая страницу."""
    global DRIVER
    try:
        DRIVER.delete_all_cookies()

        DRIVER.execute_script("localStorage.clear();")
        DRIVER.execute_script("sessionStorage.clear();")

        DRIVER.get(BASE_URL)

        WebDriverWait(DRIVER, 30).until(
            ec.presence_of_element_located((By.CSS_SELECTOR, "div.relative.z-10 textarea"))
        )
        time.sleep(2)

        logger.debug("Страница загружена, сессия обновлена.")
    except Exception as e:
        logger.debug(f"Ошибка при перезапуске сессии: {e}")

def close_driver():
    global DRIVER
    if DRIVER:
        DRIVER.quit()
        logger.debug("Браузер закрыт.")
    DRIVER = None

def minimize():
    try:
        DRIVER.minimize_window()
    except Exception as e:
        logger.debug(f"Не удалось свернуть браузер: {e}")
