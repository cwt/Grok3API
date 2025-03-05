import asyncio

from aiogram.fsm.storage.memory import MemoryStorage

from aiogram import Bot, Dispatcher
from aiogram.types import Message, BufferedInputFile
from grok3api.client import GrokClient
from file_tools import BOT_TOKEN, ALLOWED_USER_IDS
from file_tools import MESSAGE_HISTORY_COUNT, PERSONALITY
from log_tools import logger

GROK_CLIENT: GrokClient
storage = MemoryStorage()
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

async def send_long_message(chat_id, text, max_length=4000):
    """Отправляет текст, разбивая его на части, если он длиннее max_length."""
    if len(text) <= max_length:
        try:
            await bot.send_message(chat_id, text, parse_mode="Markdown")
        except Exception as e:
            logger.error(f'Ошибка при отправке сообщения с Markdown, переключаю на HTML: {e}')
            await bot.send_message(chat_id, text, parse_mode="HTML")
        GROK_CLIENT.history.save_history()
    else:
        parts = []
        while len(text) > 0:
            if len(text) <= max_length:
                parts.append(text)
                break
            split_pos = text.rfind(' ', 0, max_length)
            if split_pos == -1:
                split_pos = max_length
            parts.append(text[:split_pos])
            text = text[split_pos:].lstrip()
        for part in parts:
            try:
                await bot.send_message(chat_id, part, parse_mode="Markdown")
            except Exception as e:
                logger.error(f'Ошибка при отправке части сообщения с Markdown, переключаю на HTML: {e}')
                await bot.send_message(chat_id, part, parse_mode="HTML")
        GROK_CLIENT.history.save_history()

@dp.message()
async def handle_message(message: Message):
    """Обработчик входящих сообщений"""
    user_id = message.from_user.id if message.from_user else None
    chat_id = str(message.chat.id)

    if user_id not in ALLOWED_USER_IDS:
        logger.info(f'Игнорирую сообщение от {user_id}')
        return

    try:
        await bot.send_chat_action(chat_id=message.chat.id, action="typing")
        response = GROK_CLIENT.send_message(message.text, chat_id)
        text_response = response.modelResponse.message

        await send_long_message(message.chat.id, text_response)

        if response.modelResponse.generatedImages:
            for img in response.modelResponse.generatedImages:
                await bot.send_chat_action(chat_id=message.chat.id, action="upload_photo")
                image_file = img.download()
                image_file.seek(0)
                input_photo = BufferedInputFile(image_file.read(), filename="image.jpg")
                await bot.send_photo(chat_id=message.chat.id, photo=input_photo)

    except Exception as e:
        logger.error(f'Ошибка: {e}')
        await message.answer('Произошла ошибка при обработке запроса.')
        await bot.send_chat_action(chat_id=message.chat.id, action="cancel")

async def main():
    """Основная функция запуска бота"""
    global GROK_CLIENT
    GROK_CLIENT = GrokClient(history_msg_count=MESSAGE_HISTORY_COUNT)
    GROK_CLIENT.history.load_history()
    GROK_CLIENT.history.set_main_system_prompt(PERSONALITY)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())