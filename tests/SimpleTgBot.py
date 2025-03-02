import os
import logging
from logging.handlers import RotatingFileHandler
import asyncio

from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
from aiogram.types import Message, BufferedInputFile
from aiogram.filters import Command
from grok3.client import GrokClient

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        RotatingFileHandler("bot.log", maxBytes=2 * 1024 * 1024, backupCount=5, encoding="utf-8"),  # Лог ограничен 2MB, хранится 5 копий
        logging.StreamHandler()
    ]
)

GROK_CLIENT: GrokClient
logger = logging.getLogger(__name__)


if not os.path.exists('env'):
    with open('env', 'w') as f:
        f.write('BOT_BOT_TOKEN=\n')
        f.write('BOT_ALLOWED_USER_IDS=\n')
        f.write('BOT_MESSAGE_HISTORY_COUNT=10\n')
        f.write('BOT_PERSONALITY=\n')
    logger.info('Файл env создан с пустыми значениями. Заполните необходимые поля.')
    exit(1)

load_dotenv()

BOT_TOKEN = os.getenv('BOT_BOT_TOKEN')
ALLOWED_USER_IDS = os.getenv('BOT_ALLOWED_USER_IDS')
MESSAGE_HISTORY_COUNT = int(os.getenv('BOT_MESSAGE_HISTORY_COUNT', 10))
PERSONALITY = os.getenv('BOT_PERSONALITY', "")

if not BOT_TOKEN:
    logger.error('BOT_BOT_TOKEN не установлен в env')
    exit(1)

if not ALLOWED_USER_IDS:
    logger.error('BOT_ALLOWED_USER_IDS не установлен в env')
    exit(1)

ALLOWED_USER_IDS = [int(uid.strip()) for uid in ALLOWED_USER_IDS.split()]

storage = MemoryStorage()
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


@dp.message()
async def handle_message(message: Message, state: FSMContext):
    """Обработчик входящих сообщений с хранением истории в FSM"""
    user_id = message.from_user.id
    chat_id = message.chat.id

    if user_id not in ALLOWED_USER_IDS:
        logger.info(f'Игнорирую сообщение от {user_id}')
        return

    try:
        data = await state.get_data()
        chat_histories = data.get("chat_histories", {})

        chat_history = chat_histories.get(chat_id, [])

        chat_history.append({'role': 'user', 'content': message.text})

        if len(chat_history) > MESSAGE_HISTORY_COUNT:
            chat_history = chat_history[-MESSAGE_HISTORY_COUNT:]

        chat_histories[chat_id] = chat_history
        await state.update_data(chat_histories=chat_histories)

        formatted_history = PERSONALITY + "\n".join(f"{msg['role']}: {msg['content']}" for msg in chat_history)
        response = GROK_CLIENT.ChatCompletion.create(formatted_history)
        text_response = response.modelResponse.message

        await message.answer(text_response, parse_mode="Markdown")


        if response.modelResponse.generatedImages:
            for img in response.modelResponse.generatedImages:
                image_file = img.download()
                image_file.seek(0)
                input_photo = BufferedInputFile(image_file.read(), filename="image.jpg")

                await bot.send_photo(chat_id=message.chat.id, photo=input_photo)

        chat_history.append({'role': 'assistant', 'content': text_response})
        chat_histories[chat_id] = chat_history[-MESSAGE_HISTORY_COUNT:]
        await state.update_data(chat_histories=chat_histories)

    except Exception as e:
        logger.error(f'Ошибка: {e}')
        await message.answer('Произошла ошибка при обработке запроса.')

@dp.message(Command("start"))
async def start_handler(message: Message):
    """Обработчик команды /start"""
    await message.answer("Привет! Отправьте сообщение, и я вам отвечу.")

async def main():
    """Основная функция запуска бота"""
    global GROK_CLIENT
    GROK_CLIENT = GrokClient()
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
