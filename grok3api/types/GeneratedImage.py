import asyncio
from io import BytesIO
from dataclasses import dataclass
from typing import Optional, List

from grok3api.logger import logger
from grok3api import driver

try:
    import aiofiles
    AIOFILES_AVAILABLE = True
except ImportError:
    AIOFILES_AVAILABLE = False

@dataclass
class GeneratedImage:
    url: str
    _base_url: str = "https://assets.grok.com"
    cookies: Optional[List[dict]] = None

    def __post_init__(self):
        """
        After initialization, check driver.DRIVER and get cookies for _base_url,
        if the driver is available. Otherwise, save cookies as None.
        """
        if driver.web_driver is not None:
            # self.cookies = driver.web_driver.get_cookies()
            self.cookies = driver.web_driver._driver.get_cookies()
        else:
            self.cookies = None

    def download(self, timeout: int = driver.web_driver.TIMEOUT) -> Optional[BytesIO]:
        """Method to download an image into memory through the browser with a timeout."""
        try:
            image_data = self._fetch_image(timeout=timeout)
            if image_data is None:
                return None
            image_buffer = BytesIO(image_data)
            image_buffer.seek(0)
            return image_buffer
        except Exception as e:
            logger.error(f"Error while downloading the image (download): {e}")
            return None

    # async def async_download(self, timeout: int = 20) -> Optional[BytesIO]:
    #     """Asynchronous method to download an image into memory with a timeout.
    #
    #     Args:
    #         timeout (int): Timeout in seconds (default is 20).
    #
    #     Returns:
    #         Optional[BytesIO]: BytesIO object with image data or None in case of an error.
    #     """
    #     try:
    #         image_data = await asyncio.to_thread(self._fetch_image, timeout=timeout, proxy=driver.web_driver.def_proxy)
    #         if image_data is None:
    #             return None
    #         image_buffer = BytesIO(image_data)
    #         image_buffer.seek(0)
    #         return image_buffer
    #     except Exception as e:
    #         logger.error(f"Error while downloading the image (download): {e}")
    #         return None
    #
    # async def async_save_to(self, path: str, timeout: int = 10) -> None:
    #     """Asynchronously downloads the image and saves it to a file with a timeout.
    #
    #     Args:
    #         path (str): Path to save the file.
    #         timeout (int): Timeout in seconds (default is 10).
    #     """
    #     try:
    #         logger.debug(f"Attempting to save the image to a file: {path}")
    #         image_data = await asyncio.to_thread(self._fetch_image, timeout=timeout, proxy=driver.web_driver.def_proxy)
    #         image_data = BytesIO(image_data)
    #         if image_data is not None:
    #             if AIOFILES_AVAILABLE:
    #                 async with aiofiles.open(path, "wb") as f:
    #                     await f.write(image_data.getbuffer())
    #             else:
    #                 def write_file_sync(file_path: str, data: BytesIO):
    #                     with open(file_path, "wb") as file:
    #                         file.write(data.getbuffer())
    #
    #                 await asyncio.to_thread(write_file_sync, path, image_data)
    #             logger.debug(f"Image successfully saved to: {path}")
    #         else:
    #             logger.error("The image was not downloaded, saving canceled.")
    #     except Exception as e:
    #         logger.error(f"In save_to: {e}")

    def download_to(self, path: str, timeout: int = driver.web_driver.TIMEOUT) -> None:
        """Downloads the image to a file through the browser with a timeout."""
        try:
            image_data = self._fetch_image(timeout=timeout)
            if image_data is not None:
                with open(path, "wb") as f:
                    f.write(image_data)
                logger.debug(f"Image saved to: {path}")
            else:
                logger.debug("The image was not downloaded, saving canceled.")
        except Exception as e:
            logger.error(f"Error while saving to a file: {e}")

    def save_to(self, path: str, timeout: int = driver.web_driver.TIMEOUT) -> bool:
        """Downloads the image using download() and saves it to a file with a timeout."""
        try:
            logger.debug(f"Attempting to save the image to a file: {path}")
            image_data = self.download(timeout=timeout)
            if image_data is not None:
                with open(path, "wb") as f:
                    f.write(image_data.getbuffer())
                logger.debug(f"Image successfully saved to: {path}")
                return True
            else:
                logger.debug("The image was not downloaded, saving canceled.")
                return False
        except Exception as e:
            logger.error(f"In save_to: {e}")
            return False

    def _fetch_image(self, timeout: int = driver.web_driver.TIMEOUT, proxy: Optional[str] = driver.web_driver.def_proxy) -> Optional[bytes]:
        """Private function to download an image through the browser with a timeout."""
        if not self.cookies or len(self.cookies) == 0:
            logger.debug("No cookies for image download.")
            return None

        image_url = self.url if self.url.startswith('/') else '/' + self.url
        full_url = self._base_url + image_url
        logger.debug(f"Full URL for image download: {full_url}, timeout: {timeout} sec")

        fetch_script = f"""
        console.log("Starting fetch with credentials: 'include'");
        console.log("Cookies in browser before fetch:", document.cookie);

        const request = fetch('{full_url}', {{
            method: 'GET'
        }})
        .then(response => {{
            console.log("Response status:", response.status);
            console.log("Response headers:", Array.from(response.headers.entries()));
            const contentType = response.headers.get('Content-Type');
            if (!response.ok) {{
                console.log("Request failed with status:", response.status);
                return 'Error: HTTP ' + response.status;
            }}
            if (!contentType || !contentType.startsWith('image/')) {{
                return response.text().then(text => {{
                    console.log("Invalid MIME type detected:", contentType);
                    console.log("Response content:", text);
                    return 'Error: Invalid MIME type: ' + contentType + ', content: ' + text;
                }});
            }}
            return response.arrayBuffer();
        }})
        .then(buffer => {{
            console.log("Image data received, length:", buffer.byteLength);
            return Array.from(new Uint8Array(buffer));
        }})
        .catch(error => {{
            console.log("Fetch error:", error.toString());
            return 'Error: ' + error;
        }});

        console.log("Fetch request sent, awaiting response...");
        return request;
        """
        driver.web_driver.init_driver(wait_loading=False)
        try:
            try:
                for cookie in self.cookies:
                    if 'name' in cookie and 'value' in cookie:
                        if 'domain' not in cookie or not cookie['domain']:
                            cookie['domain'] = '.grok.com'
                        driver.web_driver.add_cookie(cookie)
                    else:
                        logger.warning(f"Skipped invalid cookie: {cookie}")
                logger.debug(f"Cookies set: {self.cookies}")
            except Exception as e:
                logger.error(f"Error while setting cookies: {e}")
                return None

            driver.web_driver.get(full_url)
            response = driver.web_driver.execute_script(fetch_script)
            if response and 'This service is not available in your region' in response:
                driver.web_driver.set_proxy(proxy)
                driver.web_driver.get(full_url)
                response = driver.web_driver.execute_script(fetch_script)
            driver.web_driver.get(driver.web_driver.BASE_URL)
        except Exception as e:
            logger.error(f"Error executing script in the browser: {e}")
            return None

        if isinstance(response, str) and response.startswith('Error:'):
            logger.error(f"Error while downloading the image: {response}")
            return None

        image_data = bytes(response)
        logger.debug("Image successfully downloaded through the browser.")
        return image_data
