import logging
import re
import time
from typing import Optional
import os
import shutil
import subprocess
import atexit
import signal
import sys

from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.webdriver import WebDriver as ChromeWebDriver
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.common.exceptions import SessionNotCreatedException

from grok3api.grok3api_logger import logger

def hide_unnecessary_logs():
    try:
        uc_logger = logging.getLogger("undetected_chromedriver")
        for handler in uc_logger.handlers[:]:
            uc_logger.removeHandler(handler)
        uc_logger.setLevel(logging.CRITICAL)

        selenium_logger = logging.getLogger("selenium")
        for handler in selenium_logger.handlers[:]:
            selenium_logger.removeHandler(handler)
        selenium_logger.setLevel(logging.CRITICAL)

        logging.getLogger("selenium.webdriver").setLevel(logging.CRITICAL)
        logging.getLogger("selenium.webdriver.remote.remote_connection").setLevel(logging.CRITICAL)
    except KeyboardInterrupt:
        raise
    except Exception as e:
        logging.debug(f"Ошибка при подавлении логов (hide_unnecessary_logs): {e}")
hide_unnecessary_logs()


DRIVER: Optional[ChromeWebDriver] = None
TIMEOUT = 120
USE_XVFB = True
BASE_URL = "https://grok.com/"
CHROME_VERSION = None
WAS_FATAL = False

def safe_del(self):
    try:
        try:
            if hasattr(self, 'service') and self.service.process:
                self.service.process.kill()
                logger.debug("Процесс сервиса ChromeDriver успешно завершен.")
        except Exception as e:
            logger.debug(f"Ошибка при завершении процесса сервиса: {e}")
        try:
            self.quit()
            logger.debug("ChromeDriver успешно закрыт через quit().")
        except Exception as e:
            logger.debug(f"uc.Chrome.__del__: при вызове quit(): {e}")

    except Exception as e:
        logger.error(f"uc.Chrome.__del__: {e}")
try:
    uc.Chrome.__del__ = safe_del
except:
    pass

def init_driver(wait_loading: bool = True,
                use_xvfb: bool = True,
                timeout: Optional[int] = None):
    """Запускает ChromeDriver и проверяет/устанавливает базовый URL."""
    try:
        global DRIVER, USE_XVFB
        driver_timeout = timeout if timeout is not None else TIMEOUT
        USE_XVFB = use_xvfb
        if USE_XVFB:
            safe_start_xvfb()

        if DRIVER:
            minimize()
            current_url = DRIVER.current_url
            if current_url != BASE_URL:
                logger.debug(f"Текущий URL ({current_url}) не совпадает с базовым ({BASE_URL}), переходим...")
                DRIVER.get(BASE_URL)
                if wait_loading:
                    logger.debug("Ждём появления поля ввода после перехода...")
                    WebDriverWait(DRIVER, driver_timeout).until(
                        ec.presence_of_element_located((By.CSS_SELECTOR, "div.relative.z-10 textarea"))
                    )
                    logger.debug("Поле ввода найдено, ждём ещё 2 секунды...")
                    time.sleep(2)
            return



        def create_driver():
            """Создаёт новый экземпляр ChromeDriver с новой ChromeOptions"""
            chrome_options = Options()
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--incognito")
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--disable-dev-shm-usage")

            new_driver = uc.Chrome(options=chrome_options, headless=False, use_subprocess=False, version_main=CHROME_VERSION)
            new_driver.set_script_timeout(driver_timeout)
            return new_driver

        try:
            DRIVER = create_driver()
        except SessionNotCreatedException as e:
            close_driver()
            error_message = str(e)

            match = re.search(r"Current browser version is (\d+)", error_message)

            if match:
                current_version = int(match.group(1))
            else:
                current_version = get_chrome_version()
            global CHROME_VERSION
            CHROME_VERSION = current_version
            logger.info(
                f"Несовместимость браузера и драйвера, пробуем переустановить драйвер для Chrome {CHROME_VERSION}...")
            DRIVER = create_driver()
            logger.info(f"Удалось установить версию драйвера на {CHROME_VERSION}.")

        minimize()
        DRIVER.get(BASE_URL)
        if wait_loading:
            logger.debug("Ждём появления поля ввода...")
            WebDriverWait(DRIVER, driver_timeout).until(
                ec.presence_of_element_located((By.CSS_SELECTOR, "div.relative.z-10 textarea"))
            )
            logger.debug("Поле ввода найдено, ждём ещё 2 секунды...")
            time.sleep(2)
        logger.debug("Браузер запущен.")

    except Exception as e:
        logger.fatal(f"Ошибка в init_driver: {e}")
        global WAS_FATAL
        if not WAS_FATAL:
            WAS_FATAL = True
            init_driver()
        else: raise e


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


def safe_start_xvfb():
    """Запускает Xvfb, если он ещё не запущен, для работы Chrome без GUI на Linux."""
    if not sys.platform.startswith("linux"):
        return

    if shutil.which("google-chrome") is None and shutil.which("chrome") is None:
        logger.error("Chrome не установлен, не удается обновить куки. Установите Chrome.")
        return

    if shutil.which("Xvfb") is None:
        logger.error("Xvfb не установлен! Установите его командой: sudo apt install xvfb")
        raise RuntimeError("Xvfb отсутствует")

    result = subprocess.run(["pgrep", "-f", "Xvfb :99"], capture_output=True, text=True)
    if not result.stdout.strip():
        logger.debug("Запускаем Xvfb...")
        subprocess.Popen(["Xvfb", ":99", "-screen", "0", "800x600x8"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        for _ in range(10):
            time.sleep(1)
            result = subprocess.run(["pgrep", "-f", "Xvfb :99"], capture_output=True, text=True)
            if result.stdout.strip():
                logger.debug("Xvfb успешно запущен.")
                os.environ["DISPLAY"] = ":99"
                time.sleep(2)
                return
        logger.error("Xvfb не запустился за 10 секунд! Проверьте логи системы.")
        raise RuntimeError("Не удалось запустить Xvfb")
    else:
        logger.debug("Xvfb уже запущен.")
        os.environ["DISPLAY"] = ":99"

def get_chrome_version():
    """Определяет текущую версию установленного Chrome."""
    import subprocess
    import platform

    if platform.system() == "Windows":
        cmd = r'wmic datafile where name="C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe" get Version /value'
    else:
        cmd = r'google-chrome --version'

    try:
        output = subprocess.check_output(cmd, shell=True, text=True).strip()
        version = re.search(r"(\d+)\.", output).group(1)
        return int(version)
    except Exception as e:
        print(f"Ошибка при получении версии Chrome: {e}")
        return None


atexit.register(close_driver)
def signal_handler(sig, frame):
    logger.debug("Остановка...")
    close_driver()
    sys.exit(0)
signal.signal(signal.SIGINT, signal_handler)
