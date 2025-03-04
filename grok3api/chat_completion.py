import json
from typing import Any

from grok3api.grok3api_logger import logger
from grok3api.types.GrokResponse import GrokResponse
from grok3api import driver


class ChatCompletion:
    NEW_CHAT_URL = "https://grok.com/rest/app-chat/conversations/new"

    def __init__(self, use_xvfb: bool = True):
        self.use_xvfb = use_xvfb

    def _send_request(self, payload, headers, timeout=driver.TIMEOUT):
        """Отправляем запрос через браузер с таймаутом, с ограничением на 3 попытки."""
        max_tries = 3

        try_index = 0
        while try_index < max_tries:
            try:
                logger.debug(
                    f"Отправляем запрос (попытка {try_index + 1}): headers={headers}, payload={payload}, timeout={timeout} секунд")

                fetch_script = f"""
                const controller = new AbortController();
                const signal = controller.signal;
                const timeoutId = setTimeout(() => controller.abort(), {timeout * 1000});

                const payload = {json.dumps(payload)};
                return fetch('{self.NEW_CHAT_URL}', {{
                    method: 'POST',
                    headers: {json.dumps(headers)},
                    body: JSON.stringify(payload),
                    credentials: 'include',
                    signal: signal
                }})
                .then(response => {{
                    clearTimeout(timeoutId);
                    if (!response.ok) {{
                        return response.text().then(text => 'Error: HTTP ' + response.status + ' - ' + text);
                    }}
                    return response.text();
                }})
                .catch(error => {{
                    clearTimeout(timeoutId);
                    if (error.name === 'AbortError') {{
                        return 'TimeoutError';
                    }}
                    return 'Error: ' + error;
                }});
                """

                driver.init_driver(use_xvfb=self.use_xvfb)
                response = driver.DRIVER.execute_script(fetch_script)

                if response == 'TimeoutError':
                    logger.error(f"Запрос превысил таймаут {timeout} секунд.")
                    break
                elif isinstance(response, str) and response.startswith('Error:'):
                    error_msg = response
                    logger.error(f"Ошибка: {error_msg}")
                    if '429' in error_msg or 'Unauthorized' in error_msg or "Too Many Requests" in error_msg:
                        if try_index < max_tries - 1:
                            logger.debug("Словили 429 или Unauthorized, перезапускаем сессию...")
                            driver.restart_session()
                            try_index += 1
                            continue
                        else:
                            logger.error(f"Превышен лимит попыток ({max_tries}) для ошибки: {error_msg}")
                    break
                else:
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
                logger.error(f"Ошибка: {e}")
                break
        return {}

    def create(self, message: str, **kwargs: Any) -> GrokResponse:
        """
        Отправляет запрос к API Grok с одним сообщением и дополнительными параметрами.

        Args:
            message (str): Сообщение пользователя для отправки в API.
            **kwargs: Дополнительные параметры для настройки запроса.

        Keyword Args:
            timeout (int): Таймаут одного ожидания получения ответа. По умолчанию: 45
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

            excluded_keys = {"auto_update_cookie", "cookies_file", "timeout", message}
            filtered_kwargs = {}
            for key, value in kwargs.items():
                if key not in excluded_keys:
                    filtered_kwargs[key] = value

            payload.update(filtered_kwargs)

            logger.debug(f"Grok payload: {payload}")

            response_json = self._send_request(payload, headers, timeout)

            if isinstance(response_json, dict):
                return GrokResponse(response_json)

            logger.error("В create: неожиданный формат ответа от сервера")
            return GrokResponse(response_json)
        except Exception as e:
            logger.error(f"В create: {e}")
            return GrokResponse({})
