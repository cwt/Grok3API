import asyncio
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage

from aiogram import Bot, Dispatcher
from aiogram.types import Message, BufferedInputFile
from grok3api.client import GrokClient
from tests.SimpleTgBot.file_tools import BOT_TOKEN, ALLOWED_USER_IDS, load_chat_histories
from tests.SimpleTgBot.file_tools import MESSAGE_HISTORY_COUNT, save_chat_histories, PERSONALITY
from tests.SimpleTgBot.log_tools import logger

GROK_CLIENT: GrokClient
storage = MemoryStorage()
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

async def send_long_message(chat_id, text, max_length=4000):
    """Отправляет текст, разбивая его на части, если он длиннее max_length."""
    if len(text) <= max_length:
        await bot.send_message(chat_id, text, parse_mode="Markdown")
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
            await bot.send_message(chat_id, part, parse_mode="Markdown")

@dp.message()
async def handle_message(message: Message, state: FSMContext):
    """Обработчик входящих сообщений с хранением истории в FSM и файле"""
    user_id = message.from_user.id
    chat_id = str(message.chat.id)

    if user_id not in ALLOWED_USER_IDS:
        logger.info(f'Игнорирую сообщение от {user_id}')
        return

    try:
        data = await state.get_data()
        chat_histories = data.get("chat_histories", load_chat_histories())

        chat_history = chat_histories.get(chat_id, [])
        chat_history.append({'role': 'user', 'content': message.text})

        if len(chat_history) > MESSAGE_HISTORY_COUNT:
            chat_history = chat_history[-MESSAGE_HISTORY_COUNT:]

        chat_histories[chat_id] = chat_history
        await state.update_data(chat_histories=chat_histories)

        formatted_history = PERSONALITY + "\n".join(f"{msg['role']}: {msg['content']}" for msg in chat_history)

        await bot.send_chat_action(chat_id=message.chat.id, action="typing")
        response = GROK_CLIENT.ChatCompletion.create(formatted_history)
        text_response = response.modelResponse.message

        await send_long_message(message.chat.id, text_response)

        if response.modelResponse.generatedImages:
            await bot.send_chat_action(chat_id=message.chat.id, action="upload_photo")
            for img in response.modelResponse.generatedImages:
                image_file = img.download()
                image_file.seek(0)
                input_photo = BufferedInputFile(image_file.read(), filename="image.jpg")
                await bot.send_photo(chat_id=message.chat.id, photo=input_photo)

        chat_history.append({'role': 'assistant', 'content': text_response})
        chat_histories[chat_id] = chat_history[-MESSAGE_HISTORY_COUNT:]
        await state.update_data(chat_histories=chat_histories)

        save_chat_histories(chat_histories)

    except Exception as e:
        logger.error(f'Ошибка: {e}')
        await message.answer('Произошла ошибка при обработке запроса.')
        await bot.send_chat_action(chat_id=message.chat.id, action="cancel")


async def main():
    """Основная функция запуска бота"""
    global GROK_CLIENT
    GROK_CLIENT = GrokClient()
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())