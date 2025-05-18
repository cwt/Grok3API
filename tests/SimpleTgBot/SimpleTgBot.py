import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message
from grok3api.client import GrokClient

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("aiogram")

BOT_TOKEN = "BOT_TOKEN"

bot = Bot(token=BOT_TOKEN)
router = Router()
dp = Dispatcher()

@router.message(~F.text.startswith("/"))
async def handle_message(message: Message):
    """Обрабатывает текст."""
    if not message.text:
        await message.answer("Пустое сообщение.")
        return

    try:
        response = await GROK_CLIENT.async_ask(message=message.text, history_id=str(message.chat.id))
        text_response = response.modelResponse.message if response.modelResponse else ""
        await message.answer(text_response)
    except Exception as e:
        print(f"Ошибка: {e}")
        await message.answer("Ошибка.")

@router.message(Command("clear"))
async def handle_clear_command(message: Message):
    """Очищает историю."""
    try:
        GROK_CLIENT.history.del_history_by_id(str(message.chat.id))
        await message.answer("История очищена.")
    except Exception as e:
        print(f"Ошибка: {e}")
        await message.answer("Ошибка очистки.")

async def main():
    """Запускает бота."""
    dp.include_router(router)
    await dp.start_polling(bot)

if __name__ == "__main__":
    GROK_CLIENT = GrokClient(
        history_msg_count=10,
        main_system_prompt="Отвечай только матом"
    )
    asyncio.run(main())