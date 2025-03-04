import os
import json
from dotenv import load_dotenv

from tests.SimpleTgBot.log_tools import logger

HISTORY_FILE = "chat_histories.json"

def load_chat_histories():
    """Загружает историю чатов из файла."""
    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError:
        logger.error("Ошибка при чтении файла истории.")
        return {}

def save_chat_histories(chat_histories):
    """Сохраняет историю чатов в файл."""
    try:
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(chat_histories, f, ensure_ascii=False, indent=4)
    except Exception as e:
        logger.error(f"Ошибка при сохранении истории: {e}")

if not os.path.exists('.env'):
    with open('.env', 'w') as f:
        f.write('BOT_BOT_TOKEN=\n')
        f.write('BOT_ALLOWED_USER_IDS=\n')
        f.write('BOT_MESSAGE_HISTORY_COUNT=10\n')
        f.write('BOT_PERSONALITY=\n')
    logger.info('Файл .env создан с пустыми значениями. Заполните необходимые поля.')
    exit(1)

load_dotenv()

BOT_TOKEN = os.getenv('BOT_BOT_TOKEN')
ALLOWED_USER_IDS = os.getenv('BOT_ALLOWED_USER_IDS')
MESSAGE_HISTORY_COUNT = int(os.getenv('BOT_MESSAGE_HISTORY_COUNT', 10))
PERSONALITY = os.getenv('BOT_PERSONALITY', "")

if not BOT_TOKEN:
    logger.error('BOT_BOT_TOKEN не установлен в .env')
    exit(1)

if not ALLOWED_USER_IDS:
    logger.error('BOT_ALLOWED_USER_IDS не установлен в .env')
    exit(1)

ALLOWED_USER_IDS = [int(uid.strip()) for uid in ALLOWED_USER_IDS.split(';')]
