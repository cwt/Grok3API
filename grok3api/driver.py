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

from grok3api.logger import logger

class WebDriverSingleton:
    """Singleton for managing ChromeDriver."""
    _instance = None
    _driver: Optional[ChromeWebDriver] = None
    TIMEOUT = 360

    USE_XVFB = True
    xvfb_display: Optional[int] = None

    BASE_URL = "https://grok.com/"
    CHROME_VERSION = None
    WAS_FATAL = False
    def_proxy = "socks4://68.71.252.38:4145"

    execute_script = None
    add_cookie = None
    get_cookies = None
    get = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(WebDriverSingleton, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        self._hide_unnecessary_logs()
        self._patch_chrome_del()
        atexit.register(self.close_driver)
        signal.signal(signal.SIGINT, self._signal_handler)

    def _hide_unnecessary_logs(self):
        """Suppresses unnecessary logs."""
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
            logging.debug(f"Error while suppressing logs (_hide_unnecessary_logs): {e}")

    def _patch_chrome_del(self):
        """Patches the __del__ method for uc.Chrome."""
        def safe_del(self):
            try:
                try:
                    if hasattr(self, 'service') and self.service.process:
                        self.service.process.kill()
                        logger.debug("ChromeDriver service process successfully terminated.")
                except Exception as e:
                    logger.debug(f"Error while terminating service process: {e}")
                try:
                    self.quit()
                    logger.debug("ChromeDriver successfully closed via quit().")
                except Exception as e:
                    logger.debug(f"uc.Chrome.__del__: error during quit(): {e}")
            except Exception as e:
                logger.error(f"uc.Chrome.__del__: {e}")
        try:
            uc.Chrome.__del__ = safe_del
        except:
            pass

    def _is_driver_alive(self, driver):
        """Checks if the driver is alive."""
        try:
            driver.title
            return True
        except:
            return False

    def _setup_driver(self, driver, wait_loading: bool, timeout: int):
        """Sets up the driver: minimizes, loads the base URL, and waits for the input field."""
        self._minimize()
        driver.get(self.BASE_URL)
        if wait_loading:
            logger.debug("Waiting for page load with implicit wait...")
            try:
                WebDriverWait(driver, timeout).until(
                    ec.presence_of_element_located((By.CSS_SELECTOR, "div.relative.z-10 textarea"))
                )
                time.sleep(2)
                logger.debug("Input field found.")
            except Exception:
                logger.debug("Input field not found")

    def init_driver(self, wait_loading: bool = True, use_xvfb: bool = True, timeout: Optional[int] = None, proxy: Optional[str] = None):
        """Starts ChromeDriver and checks/sets the base URL with three attempts."""
        driver_timeout = timeout if timeout is not None else self.TIMEOUT

        self.USE_XVFB = use_xvfb
        attempts = 0
        max_attempts = 3

        def _create_driver():
            chrome_options = Options()
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--incognito")
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--disable-dev-shm-usage")
            if proxy:
                logger.debug(f"Adding proxy to options: {proxy}")
                chrome_options.add_argument(f"--proxy-server={proxy}")

            new_driver = uc.Chrome(options=chrome_options, headless=False, use_subprocess=True, version_main=self.CHROME_VERSION)
            new_driver.set_script_timeout(driver_timeout)
            return new_driver

        while attempts < max_attempts:
            try:
                if self.USE_XVFB:
                    self._safe_start_xvfb()

                if self._driver and self._is_driver_alive(self._driver):
                    self._minimize()
                    current_url = self._driver.current_url
                    if current_url != self.BASE_URL:
                        logger.debug(f"Current URL ({current_url}) does not match base URL ({self.BASE_URL}), navigating...")
                        self._driver.get(self.BASE_URL)
                        if wait_loading:
                            logger.debug("Waiting for page load with implicit wait...")
                            try:
                                WebDriverWait(self._driver, driver_timeout).until(
                                    ec.presence_of_element_located((By.CSS_SELECTOR, "div.relative.z-10 textarea"))
                                )
                                time.sleep(2)
                                logger.debug("Input field found.")
                            except Exception:
                                logger.error("Input field not found.")
                    self.WAS_FATAL = False
                    logger.debug("Driver is alive, all good.")

                    self.execute_script = self._driver.execute_script
                    self.add_cookie = self._driver.add_cookie
                    self.get_cookies = self._driver.get_cookies
                    self.get = self._driver.get

                    return

                logger.debug(f"Attempt {attempts + 1}: creating new driver...")

                self.close_driver()
                self._driver = _create_driver()
                self._setup_driver(self._driver, wait_loading, driver_timeout)
                self.WAS_FATAL = False

                logger.debug("Browser started")

                self.execute_script = self._driver.execute_script
                self.add_cookie = self._driver.add_cookie
                self.get_cookies = self._driver.get_cookies
                self.get = self._driver.get

                return

            except SessionNotCreatedException as e:
                self.close_driver()
                error_message = str(e)
                match = re.search(r"Current browser version is (\d+)", error_message)
                if match:
                    current_version = int(match.group(1))
                else:
                    current_version = self._get_chrome_version()
                self.CHROME_VERSION = current_version
                logger.info(f"Browser and driver incompatibility, attempting to reinstall driver for Chrome {self.CHROME_VERSION}...")
                self._driver = _create_driver()
                self._setup_driver(self._driver, wait_loading, driver_timeout)
                logger.info(f"Successfully set driver version to {self.CHROME_VERSION}.")
                self.WAS_FATAL = False

                self.execute_script = self._driver.execute_script
                self.add_cookie = self._driver.add_cookie
                return

            except Exception as e:
                logger.error(f"In attempt {attempts + 1}: {e}")
                attempts += 1
                self.close_driver()
                if attempts == max_attempts:
                    logger.fatal(f"All {max_attempts} attempts failed: {e}")
                    self.WAS_FATAL = True
                    raise e
                logger.debug("Waiting 1 second before next attempt...")
                time.sleep(1)

    def restart_session(self):
        """Restarts the session, clearing cookies, localStorage, sessionStorage, and reloading the page."""
        try:
            self._driver.delete_all_cookies()
            self._driver.execute_script("localStorage.clear();")
            self._driver.execute_script("sessionStorage.clear();")
            self._driver.get(self.BASE_URL)
            WebDriverWait(self._driver, 5).until(
                ec.presence_of_element_located((By.CSS_SELECTOR, "div.relative.z-10 textarea"))
            )
            time.sleep(2)
            logger.debug("Page loaded, session refreshed.")
        except Exception as e:
            logger.debug(f"Error during session restart: {e}")

    def set_cookies(self, cookies_input):
        """Sets cookies in the driver."""
        if cookies_input is None:
            return
        current_url = self._driver.current_url
        if not current_url.startswith("http"):
            raise Exception("Before setting cookies, you must first open a website in the driver!")

        if isinstance(cookies_input, str):
            cookie_string = cookies_input.strip().rstrip(";")
            cookies = cookie_string.split("; ")
            for cookie in cookies:
                if "=" not in cookie:
                    continue
                name, value = cookie.split("=", 1)
                self._driver.add_cookie({
                    "name": name,
                    "value": value,
                    "path": "/"
                })
        elif isinstance(cookies_input, dict):
            if "name" in cookies_input and "value" in cookies_input:
                cookie = cookies_input.copy()
                cookie.setdefault("path", "/")
                self._driver.add_cookie(cookie)
            else:
                for name, value in cookies_input.items():
                    self._driver.add_cookie({
                        "name": name,
                        "value": value,
                        "path": "/"
                    })
        elif isinstance(cookies_input, list):
            for cookie in cookies_input:
                if isinstance(cookie, dict) and "name" in cookie and "value" in cookie:
                    cookie = cookie.copy()
                    cookie.setdefault("path", "/")
                    self._driver.add_cookie(cookie)
                else:
                    raise ValueError("Each dictionary in the list must contain 'name' and 'value'")
        else:
            raise TypeError("cookies_input must be a string, dictionary, or list of dictionaries")

    def close_driver(self):
        """Closes the driver."""
        if self._driver:
            self._driver.quit()
            logger.debug("Browser closed.")
        self._driver = None

    def set_proxy(self, proxy: str):
        """Changes the proxy in the current driver session."""
        self.close_driver()
        self.init_driver(use_xvfb=self.USE_XVFB, timeout=self.TIMEOUT, proxy=proxy)

    def _minimize(self):
        """Minimizes the browser window."""
        try:
            self._driver.minimize_window()
        except Exception:
            pass

    def _safe_start_xvfb(self):
        """Starts Xvfb on a unique DISPLAY and saves it to an environment variable."""
        if not sys.platform.startswith("linux"):
            return

        if shutil.which("Xvfb") is None:
            logger.error("Xvfb is not installed! Install it with: sudo apt install xvfb")
            raise RuntimeError("Xvfb is missing")

        if self.xvfb_display is None:
            display_number = 99
            while True:
                result = subprocess.run(["pgrep", "-f", f"Xvfb :{display_number}"], capture_output=True, text=True)
                if not result.stdout.strip():
                    break
                display_number += 1
            self.xvfb_display = display_number

        display_var = f":{self.xvfb_display}"
        os.environ["DISPLAY"] = display_var

        result = subprocess.run(["pgrep", "-f", f"Xvfb {display_var}"], capture_output=True, text=True)
        if result.stdout.strip():
            logger.debug(f"Xvfb is already running on display {display_var}.")
            return

        logger.debug(f"Starting Xvfb on display {display_var}...")
        subprocess.Popen(["Xvfb", display_var, "-screen", "0", "1024x768x24"],
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        for _ in range(10):
            time.sleep(1)
            result = subprocess.run(["pgrep", "-f", f"Xvfb {display_var}"], capture_output=True, text=True)
            if result.stdout.strip():
                logger.debug(f"Xvfb successfully started on display {display_var}.")
                return

        raise RuntimeError(f"Xvfb failed to start on display {display_var} within 10 seconds!")

    def _get_chrome_version(self):
        """Determines the current Chrome version."""
        if "win" in sys.platform.lower():
            try:
                import winreg
                reg_path = r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\chrome.exe"
                with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, reg_path) as key:
                    chrome_path, _ = winreg.QueryValueEx(key, "")

                output = subprocess.check_output([chrome_path, "--version"], shell=True, text=True).strip()
                version = re.search(r"(\d+)\.", output).group(1)
                return int(version)
            except Exception as e:
                logger.debug(f"Failed to find Chrome version via registry: {e}")

            chrome_paths = [
                r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
            ]

            for path in chrome_paths:
                if os.path.exists(path):
                    try:
                        output = subprocess.check_output([path, "--version"], shell=True, text=True).strip()
                        version = re.search(r"(\d+)\.", output).group(1)
                        return int(version)
                    except Exception as e:
                        logger.debug(f"Error retrieving Chrome version from path {path}: {e}")
                        continue

            logger.error("Could not find Chrome or its version on Windows.")
            return None
        else:
            cmd = r'google-chrome --version'
            try:
                output = subprocess.check_output(cmd, shell=True, text=True).strip()
                version = re.search(r"(\d+)\.", output).group(1)
                return int(version)
            except Exception as e:
                logger.error(f"Error retrieving Chrome version: {e}")
                return None

    def _signal_handler(self, sig, frame):
        """Handles signals for proper termination."""
        logger.debug("Shutting down...")
        self.close_driver()
        sys.exit(0)

web_driver = WebDriverSingleton()
