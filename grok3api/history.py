import json
from typing import Dict, List, Optional
from enum import Enum

from grok3api.grok3api_logger import logger


class SenderType(Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class History:
    def __init__(self, history_msg_count: int = 0, file_path: str = "chat_histories.json"):
        self.chat_histories: Dict[str, List[Dict[str, str]]] = {}
        self.history_msg_count = history_msg_count
        self.system_prompts: Dict[str, str] = {}
        self.main_system_prompt: Optional[str] = None
        self.file_path = file_path

    def set_main_system_prompt(self, text: str):
        try:
            self.main_system_prompt = text
        except Exception as e:
            logger.error(f"В set_main_system_prompt: {e}")

    def _add_message(self, history_id: str, sender_type: SenderType, message: str):
        try:
            if self.history_msg_count < 0: self.history_msg_count = 0
            if history_id not in self.chat_histories:
                self.chat_histories[history_id] = []

            new_message = {'role': sender_type.value, 'content': message}
            self.chat_histories[history_id].append(new_message)

            max_messages = self.history_msg_count + 1
            if len(self.chat_histories[history_id]) > max_messages:
                self.chat_histories[history_id] = self.chat_histories[history_id][-max_messages:]
        except Exception as e:
            logger.error(f"В add_message: {e}")

    def _get_history(self, history_id: str) -> str:
        try:
            history = self.chat_histories.get(history_id, [])

            if history_id not in self.system_prompts and self.main_system_prompt:
                history = [{'role': SenderType.SYSTEM.value, 'content': self.main_system_prompt}] + history
            elif history_id in self.system_prompts:
                history = [{'role': SenderType.SYSTEM.value, 'content': self.system_prompts[history_id]}] + history

            return json.dumps(history, ensure_ascii=False)
        except Exception as e:
            logger.error(f"В get_history: {e}")
            return "[]"

    def set_system_prompt(self, history_id: str, text: str):
        try:
            self.system_prompts[history_id] = text
        except Exception as e:
            logger.error(f"В set_system_prompt: {e}")

    def get_system_prompt(self, history_id: str) -> str:
        try:
            return self.system_prompts.get(history_id, "")
        except Exception as e:
            logger.error(f"В get_system_prompt: {e}")
            return ""

    def save_history(self):
        try:
            with open(self.file_path, "w", encoding="utf-8") as file:
                json.dump({
                    "chat_histories": self.chat_histories,
                    "system_prompts": self.system_prompts,
                    "main_system_prompt": self.main_system_prompt
                }, file, ensure_ascii=False, indent=4)
        except Exception as e:
            logger.error(f"В save_history: {e}")

    def load_history(self):
        try:
            with open(self.file_path, "r", encoding="utf-8") as file:
                data = json.load(file)
                self.chat_histories = data.get("chat_histories", {})
                self.system_prompts = data.get("system_prompts", {})
                self.main_system_prompt = data.get("main_system_prompt", None)
        except FileNotFoundError:
            logger.info("В load_history: Файл не найден, создаем новый")
        except Exception as e:
            logger.error(f"В load_history: {e}")