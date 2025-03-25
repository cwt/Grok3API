import asyncio
import json
from typing import Any, Optional

from grok3api.history import History, SenderType
from grok3api.types.GrokResponse import GrokResponse
from grok3api import driver
from grok3api.grok3api_logger import logger


class GrokClient:
    """
    Клиент для работы с Grok.

    :param use_xvfb: Флаг для использования Xvfb. По умолчанию True. Имеет значения только на Linux.
    :param proxy: (str) URL Прокси сервера, используется только в случае региональной блокировки.
    :param history_msg_count: Количество сообщений в истории (по умолчанию `0` - сохранение истории отключено).
    :param history_path: Путь к файлу с историей в JSON-формате. По умолчанию: "chat_histories.json"
    :param history_as_json: Отправить ли в Grok историю в формате JSON (для history_msg_count > 0). По умолчанию: True
    :param history_auto_save: Автоматическая перезапись истории в файл после каждого сообщения. По умолчанию: True
    :param timeout: Максимальное время на инициализацию клиента. По умолчанию: 120 секунд
    """

    NEW_CHAT_URL = "https://grok.com/rest/app-chat/conversations/new"
    def __init__(self,
                 use_xvfb: bool = True,
                 proxy: Optional[str] = None,
                 history_msg_count: int = 0,
                 history_path: str = "chat_histories.json",
                 history_as_json: bool = True,
                 history_auto_save: bool = True,
                 timeout: int = driver.TIMEOUT):
        self.cookies_set = False
        try:
            self.proxy = proxy
            self.use_xvfb: bool = use_xvfb
            self.history = History(history_msg_count=history_msg_count,
                                   history_path=history_path,
                                   history_as_json=history_as_json)
            self.history_auto_save: bool = history_auto_save
            self.proxy_index = 0

            driver.init_driver(use_xvfb=self.use_xvfb, timeout=timeout, proxy=self.proxy)
        except Exception as e:
            logger.error(f"В GrokClient.__init__: {e}")
            raise e

    def _send_request(self,
                      payload,
                      headers,
                      timeout=driver.TIMEOUT):
        try:
            """Отправляем запрос через браузер с таймаутом."""

            headers.update({
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
                "Accept": "*/*",
                "Accept-Encoding": "gzip, deflate, br, zstd",
                "Accept-Language": "ru-RU,ru;q=0.9",
                "Content-Type": "application/json",
                "Origin": "https://grok.com",
                "Referer": "https://grok.com/",
                "Sec-Ch-Ua": '"Chromium";v="134", "Not:A-Brand";v="24", "Google Chrome";v="134"',
                "Sec-Ch-Ua-Mobile": "?0",
                "Sec-Ch-Ua-Platform": '"Windows"',
                "Sec-Fetch-Dest": "empty",
                "Sec-Fetch-Mode": "cors",
                "Sec-Fetch-Site": "same-origin",
            })

            fetch_script = f"""
            const controller = new AbortController();
            const signal = controller.signal;
            setTimeout(() => controller.abort(), {timeout * 1000});
        
            const payload = {json.dumps(payload)};
            return fetch('{self.NEW_CHAT_URL}', {{
                method: 'POST',
                headers: {json.dumps(headers)},
                body: JSON.stringify(payload),
                credentials: 'include',
                signal: signal
            }})
            .then(response => {{
                if (!response.ok) {{
                    return response.text().then(text => 'Error: HTTP ' + response.status + ' - ' + text);
                }}
                return response.text();
            }})
            .catch(error => {{
                if (error.name === 'AbortError') {{
                    return 'TimeoutError';
                }}
                return 'Error: ' + error;
            }});
            """

            response = driver.DRIVER.execute_script(fetch_script)
            if response and 'This service is not available in your region' in response:
                return 'This service is not available in your region'
            final_dict = {}
            for line in response.splitlines():
                try:
                    parsed = json.loads(line)
                    if "modelResponse" in parsed["result"]["response"]:
                        final_dict = parsed
                        break
                except (json.JSONDecodeError, KeyError):
                    continue
            logger.debug(f"Получили ответ: {final_dict}")
            return final_dict
        except Exception as e:
            logger.error(f"В _send_request: {e}")
            return {}

    def send_message(self,
            message: str,
            history_id: Optional[str] = None,
            proxy: Optional[str] = driver.def_proxy,
            **kwargs: Any) -> GrokResponse:
        """Устаревший метод отправки сообщения. Используйте ask() напрямую."""

        return self.ask(message=message,
                   history_id=history_id,
                   proxy=proxy,
                   **kwargs)

    def ask(self,
            message: str,
            history_id: Optional[str] = None,
            proxy: Optional[str] = driver.def_proxy,
            **kwargs: Any) -> GrokResponse:
        """
        Отправляет запрос к API Grok с одним сообщением и дополнительными параметрами.


        :param message: (str) Сообщение пользователя для отправки в API.
        :param history_id: (str) Идентификатор, чтобы знать, историю какого чата использовать.
        :param proxy: (str) URL Прокси сервера, используется только в случае региональной блокировки.

        Keyword Args:
            timeout (int): Таймаут ожидания получения одного ответа. По умолчанию: 120
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
            imageGenerationCount (int): Количество генерируемых изображений. По умолчанию 4.
            isPreset (bool): Указывает, является ли сообщение предустановленным. По умолчанию False. Передаётся через словарь.
            isReasoning (bool): Включить режим рассуждений в ответе модели. По умолчанию False. Передаётся через словарь.
            returnImageBytes (bool): Возвращать данные изображений в виде байтов. По умолчанию False.
            returnRawGrokInXaiRequest (bool): Возвращать необработанный вывод модели. По умолчанию False.
            sendFinalMetadata (bool): Отправлять финальные метаданные с запросом. По умолчанию True.
            toolOverrides (Dict[str, Any]): Словарь для переопределения настроек инструментов. По умолчанию пустой словарь.

        Returns:
            GrokResponse: Объект ответа от API Grok.
        """
        try:
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

            timeout = kwargs.get("timeout", driver.TIMEOUT)

            if (self.history.history_msg_count<1 and self.history.main_system_prompt is None
                    and history_id not in self.history.system_prompts):
                message_payload = message
            else:
                message_payload = self.history.get_history(history_id) + '\n' + message
                if self.history.history_msg_count > 0:
                    self.history.add_message(history_id, SenderType.ASSISTANT, message)
                    if self.history_auto_save:
                        self.history.to_file()

            payload = {
                "temporary": False,
                "modelName": "grok-3",
                "message": message_payload,
                "fileAttachments": [],
                "imageAttachments": [],
                "customInstructions": "",
                "deepsearch preset": "",
                "disableSearch": False,
                "enableImageGeneration": True,
                "enableImageStreaming": True,
                "enableSideBySide": True,
                "imageGenerationCount": 4,
                "isPreset": False,
                "isReasoning": False,
                "returnImageBytes": False,
                "returnRawGrokInXaiRequest": False,
                "sendFinalMetadata": True,
                "toolOverrides": {}
            }

            excluded_keys = {"auto_update_cookie", "cookies_file", "timeout", message}
            filtered_kwargs = {}
            for key, value in kwargs.items():
                if key not in excluded_keys:
                    filtered_kwargs[key] = value

            payload.update(filtered_kwargs)

            logger.debug(f"Grok payload: {payload}")

            max_tries = 5
            try_index = 0
            response = ""
            while try_index < max_tries:
                logger.debug(
                    f"Отправляем запрос (попытка {try_index + 1}): headers={headers}, payload={payload}, timeout={timeout} секунд")
                response = self._send_request(payload, headers, timeout)
                if isinstance(response, dict) and response:
                    response = GrokResponse(response)
                    assistant_message = response.modelResponse.message

                    if self.history.history_msg_count > 0:
                        self.history.add_message(history_id, SenderType.ASSISTANT, assistant_message)
                        if self.history_auto_save:
                            self.history.to_file()

                    return response
                try_index += 1
                driver.init_driver()
                if response and 'This service is not available in your region' in response:
                    driver.set_proxy(proxy)
                    continue
                if try_index == max_tries-1:
                    driver.close_driver()
                    driver.init_driver()
                driver.restart_session()

            logger.error("В ask: неожиданный формат ответа от сервера")
            driver.restart_session()
            return GrokResponse(response) if isinstance(response, dict) else {}
        except Exception as e:
            logger.error(f"В ask: {e}")
            return GrokResponse({})

    async def _async_send_request(self,
                            payload,
                            headers,
                            timeout=driver.TIMEOUT):
        try:
            """Отправляем запрос через браузер с таймаутом."""

            headers.update({
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
                "Accept": "*/*",
                "Accept-Encoding": "gzip, deflate, br, zstd",
                "Accept-Language": "ru-RU,ru;q=0.9",
                "Content-Type": "application/json",
                "Origin": "https://grok.com",
                "Referer": "https://grok.com/",
                "Sec-Ch-Ua": '"Chromium";v="134", "Not:A-Brand";v="24", "Google Chrome";v="134"',
                "Sec-Ch-Ua-Mobile": "?0",
                "Sec-Ch-Ua-Platform": '"Windows"',
                "Sec-Fetch-Dest": "empty",
                "Sec-Fetch-Mode": "cors",
                "Sec-Fetch-Site": "same-origin",
            })

            fetch_script = f"""
            const controller = new AbortController();
            const signal = controller.signal;
            setTimeout(() => controller.abort(), {timeout * 1000});

            const payload = {json.dumps(payload)};
            return fetch('{self.NEW_CHAT_URL}', {{
                method: 'POST',
                headers: {json.dumps(headers)},
                body: JSON.stringify(payload),
                credentials: 'include',
                signal: signal
            }})
            .then(response => {{
                if (!response.ok) {{
                    return response.text().then(text => 'Error: HTTP ' + response.status + ' - ' + text);
                }}
                return response.text();
            }})
            .catch(error => {{
                if (error.name === 'AbortError') {{
                    return 'TimeoutError';
                }}
                return 'Error: ' + error;
            }});
            """

            response = await asyncio.to_thread(driver.DRIVER.execute_script, fetch_script)
            if response and 'This service is not available in your region' in response:
                return 'This service is not available in your region'
            final_dict = {}
            for line in response.splitlines():
                try:
                    parsed = json.loads(line)
                    if "modelResponse" in parsed["result"]["response"]:
                        final_dict = parsed
                        break
                except (json.JSONDecodeError, KeyError):
                    continue
            logger.debug(f"Получили ответ: {final_dict}")
            return final_dict
        except Exception as e:
            logger.error(f"В _send_request: {e}")
            return {}

    async def async_ask(self,
                  message: str,
                  history_id: Optional[str] = None,
                  proxy: Optional[str] = driver.def_proxy,
                  **kwargs: Any) -> GrokResponse:
        """
        Отправляет запрос к API Grok с одним сообщением и дополнительными параметрами.

        :param message: (str) Сообщение пользователя для отправки в API.
        :param history_id: (str) Идентификатор, чтобы знать, историю какого чата использовать.
        :param proxy: (str) URL Прокси сервера, используется только в случае региональной блокировки.

        Keyword Args:
            timeout (int): Таймаут ожидания получения одного ответа. По умолчанию: 120
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
            imageGenerationCount (int): Количество генерируемых изображений. По умолчанию 4.
            isPreset (bool): Указывает, является ли сообщение предустановленным. По умолчанию False. Передаётся через словарь.
            isReasoning (bool): Включить режим рассуждений в ответе модели. По умолчанию False. Передаётся через словарь.
            returnImageBytes (bool): Возвращать данные изображений в виде байтов. По умолчанию False.
            returnRawGrokInXaiRequest (bool): Возвращать необработанный вывод модели. По умолчанию False.
            sendFinalMetadata (bool): Отправлять финальные метаданные с запросом. По умолчанию True.
            toolOverrides (Dict[str, Any]): Словарь для переопределения настроек инструментов. По умолчанию пустой словарь.

        Returns:
            GrokResponse: Объект ответа от API Grok.
        """
        try:
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

            timeout = kwargs.get("timeout", driver.TIMEOUT)

            if (self.history.history_msg_count < 1 and self.history.main_system_prompt is None
                    and history_id not in self.history.system_prompts):
                message_payload = message
            else:
                message_payload = self.history.get_history(history_id) + '\n' + message
                if self.history.history_msg_count > 0:
                    self.history.add_message(history_id, SenderType.ASSISTANT, message)
                    if self.history_auto_save:
                        await asyncio.to_thread(self.history.to_file)

            payload = {
                "temporary": False,
                "modelName": "grok-3",
                "message": message_payload,
                "fileAttachments": [],
                "imageAttachments": [],
                "customInstructions": "",
                "deepsearch preset": "",
                "disableSearch": False,
                "enableImageGeneration": True,
                "enableImageStreaming": True,
                "enableSideBySide": True,
                "imageGenerationCount": 4,
                "isPreset": False,
                "isReasoning": False,
                "returnImageBytes": False,
                "returnRawGrokInXaiRequest": False,
                "sendFinalMetadata": True,
                "toolOverrides": {}
            }

            excluded_keys = {"auto_update_cookie", "cookies_file", "timeout", message}
            filtered_kwargs = {}
            for key, value in kwargs.items():
                if key not in excluded_keys:
                    filtered_kwargs[key] = value

            payload.update(filtered_kwargs)

            logger.debug(f"Grok payload: {payload}")

            max_tries = 5
            try_index = 0
            response = ""
            while try_index < max_tries:
                logger.debug(
                    f"Отправляем запрос (попытка {try_index + 1}): headers={headers}, payload={payload}, timeout={timeout} секунд")
                response = await self._async_send_request(payload, headers, timeout)
                if isinstance(response, dict) and response:
                    response = GrokResponse(response)
                    assistant_message = response.modelResponse.message
                    if self.history.history_msg_count>0:
                        self.history.add_message(history_id, SenderType.ASSISTANT, assistant_message)
                        if self.history_auto_save:
                            await asyncio.to_thread(self.history.to_file)
                    return response
                try_index += 1
                await asyncio.to_thread(driver.init_driver)
                if response and 'This service is not available in your region' in response:
                    await asyncio.to_thread(driver.set_proxy, proxy)
                    continue
                if try_index == max_tries - 1:
                    await asyncio.to_thread(driver.close_driver)
                    await asyncio.to_thread(driver.init_driver)
                await asyncio.to_thread(driver.restart_session)

            logger.error("В ask: неожиданный формат ответа от сервера")
            await asyncio.to_thread(driver.restart_session)
            return GrokResponse(response) if isinstance(response, dict) else {}
        except Exception as e:
            logger.error(f"В ask: {e}")
            return GrokResponse({})