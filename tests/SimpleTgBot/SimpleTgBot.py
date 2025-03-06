import asyncio
from typing import List
import logging
from logging.handlers import RotatingFileHandler
import os
from dotenv import load_dotenv

from aiogram import Bot, Dispatcher
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, BufferedInputFile
from grok3api.client import GrokClient

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        RotatingFileHandler("bot.log", maxBytes=2 * 1024 * 1024, backupCount=2, encoding="utf-8"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)
if not os.path.exists('.env'):
    with open('.env', 'w') as f:
        f.writelines(['BOT_BOT_TOKEN=\n', 'BOT_ALLOWED_USER_IDS=\n',
                     'BOT_MESSAGE_HISTORY_COUNT=10\n', 'BOT_PERSONALITY=\n'])
    logger.info('Файл .env создан. Заполните необходимые поля.')
    exit(1)

load_dotenv()
BOT_TOKEN = os.getenv('BOT_BOT_TOKEN', None) or exit(logger.error('BOT_BOT_TOKEN не указан'))
ALLOWED_USER_IDS = [int(uid) for uid in os.getenv('BOT_ALLOWED_USER_IDS', '').split(';') if uid.strip()] or exit(logger.error('BOT_ALLOWED_USER_IDS не указан'))
MESSAGE_HISTORY_COUNT = int(os.getenv('BOT_MESSAGE_HISTORY_COUNT', 10))
PERSONALITY = os.getenv('BOT_PERSONALITY', '')

GROK_CLIENT: GrokClient
bot = Bot(token=BOT_TOKEN)
router = Router()
dp = Dispatcher()


async def send_long_message(chat_id, text, max_length=4000):
    """Отправляет текст, разбивая его на части, если он длиннее max_length."""
    logger.debug(f"Отправка сообщения в чат {chat_id}, длина текста: {len(text)}")
    if len(text) <= max_length:
        try:
            await bot.send_message(chat_id, text, parse_mode="Markdown")
            logger.debug("Сообщение отправлено")
        except Exception as e:
            logger.error(f"В send_long_message: {e}")
            await bot.send_message(chat_id, text, parse_mode="HTML")
            logger.debug("Сообщение отправлено в HTML формате")
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

        logger.debug(f"Сообщение длинное, разбито на {len(parts)} частей")

        for part in parts:
            try:
                await bot.send_message(chat_id, part, parse_mode="Markdown")
                logger.debug(f"Часть сообщения отправлена, длина: {len(part)}")

            except Exception as e:
                logger.error(f"В send_long_message: {e}")
                await bot.send_message(chat_id, part, parse_mode="HTML")
                logger.debug(f"Часть сообщения отправлена в HTML формате, длина: {len(part)}")

@router.message(~F.text.startswith("/"))
async def handle_message(message: Message):
    """Обрабатывает входящие сообщения от разрешенных пользователей."""
    if message.from_user.id not in ALLOWED_USER_IDS:
        logger.info(f"Игнорирую сообщение от пользователя {message.from_user.id}")
        return

    logger.debug(f"Получено сообщение от {message.from_user.id}: {message.text or 'без текста'}")
    chat_id = str(message.chat.id)
    msg_text = await get_media_preview(message)
    msg_text += message.text or message.caption or ""

    try:
        await bot.send_chat_action(chat_id=message.chat.id, action="typing")
        logger.debug("Отправлено действие 'typing' в чат")

        response = GROK_CLIENT.send_message(message=msg_text, history_id=chat_id)
        logger.debug("Получен ответ от GROK_CLIENT")
        text_response = response.modelResponse.message

        await send_long_message(message.chat.id, text_response)
        if response.modelResponse.generatedImages:

            logger.debug(f"Найдено {len(response.modelResponse.generatedImages)} изображений для отправки")
            for img in response.modelResponse.generatedImages:
                logger.debug("Отправка изображения в чат")
                await bot.send_chat_action(chat_id=message.chat.id, action="upload_photo")
                image_file = img.download()
                image_file.seek(0)

                input_photo = BufferedInputFile(image_file.read(), filename="image.jpg")
                await bot.send_photo(chat_id=message.chat.id, photo=input_photo)
                logger.debug("Изображение успешно отправлено")
        GROK_CLIENT.history.to_file()

    except Exception as e:

        logger.error(f"В handle_message: {e}")
        await message.answer("Произошла ошибка при обработке запроса.")

        await bot.send_chat_action(chat_id=message.chat.id, action="cancel")
        logger.debug("Действие отменено из-за ошибки")

@router.message(Command("clean"))
async def handle_clean_command(message: Message):
    """Обрабатывает команду /clean для очистки истории чата."""
    if message.from_user.id not in ALLOWED_USER_IDS:
        logger.info(f"Игнорирую команду /clean от пользователя {message.from_user.id}")
        return

    logger.debug(f"Получена команда /clean от {message.from_user.id}")
    try:
        chat_id = str(message.chat.id)

        GROK_CLIENT.history.del_history_by_id(chat_id)
        GROK_CLIENT.history.to_file()
        GROK_CLIENT.history.from_file()

        logger.debug(f"История для чата {chat_id} удалена")

        GROK_CLIENT.history.to_file()
        logger.debug("История сохранена в файл")
        await message.answer("История очищена.")
        logger.debug("Ответ об очистке отправлен")

    except Exception as e:
        logger.error(f"В handle_clean_command: {e}")
        await message.answer("Не удалось очистить историю.")
        logger.debug("Сообщение об ошибке отправлено")

async def get_media_preview(message: Message) -> str:
    try:
        placeholders: List[str] = []
        if message.photo: placeholders.append("*Фото в плохом качестве*\n")
        if message.animation: placeholders.append("*Анимация с низким качеством*\n")
        if message.video: placeholders.append("*Видео в плохом качестве*\n")
        if message.video_note: placeholders.append("*Короткое видео с низким качеством*\n")
        if message.sticker and message.sticker.thumbnail:
            placeholders.append(f"*стикер: {message.sticker.emoji}*\n" if message.sticker.emoji
                              else "*непонятный стикер*\n")
        if message.audio: placeholders.append("*Аудиофайл с низким качеством*\n")
        if message.voice: placeholders.append("*Голосовое сообщение с низким качеством*\n")
        if message.document: placeholders.append("*Документ, не удалось просмотреть*\n")
        if message.contact: placeholders.append("*Контакт, данные не отображаются*\n")
        if message.location: placeholders.append("*Местоположение, карта не доступна*\n")
        if message.venue: placeholders.append("*Место, информация не отображается*\n")
        if message.poll: placeholders.append("*Опрос, результаты не видны*\n")
        if message.dice: placeholders.append("*Кубик, значение не определено*\n")
        if message.game: placeholders.append("*Игра, превью недоступно*\n")
        if message.invoice: placeholders.append("*Счет, детали не отображаются*\n")
        if message.successful_payment: placeholders.append("*Успешная оплата, данные скрыты*\n")
        if message.passport_data: placeholders.append("*Паспортные данные, информация заблокирована*\n")
        if message.proximity_alert_triggered: placeholders.append("*Тревога о близости, данные недоступны*\n")
        if message.forum_topic_created: placeholders.append("*Тема форума создана, подробности отсутствуют*\n")
        if message.forum_topic_edited: placeholders.append("*Тема форума отредактирована, изменения не видны*\n")
        if message.forum_topic_closed: placeholders.append("*Тема форума закрыта*\n")
        if message.forum_topic_reopened: placeholders.append("*Тема форума открыта заново*\n")
        if message.video_chat_scheduled: placeholders.append("*Видеочат запланирован, время не указано*\n")
        if message.video_chat_started: placeholders.append("*Видеочат начался, доступ ограничен*\n")
        if message.video_chat_ended: placeholders.append("*Видеочат завершен*\n")
        if message.video_chat_participants_invited: placeholders.append("*Участники видеочата приглашены, список не доступен*\n")
        if message.web_app_data: placeholders.append("*Данные веб-приложения, доступ закрыт*\n")
        if message.reply_markup: placeholders.append("*Инлайн-клавиатура, кнопки не отображаются*\n")
        return "".join(placeholders) if placeholders else ""
    except Exception as e:
        logger.error(f"В get_media_preview: {e}")
        return ""


async def main():
    """Основная функция запуска бота"""
    global GROK_CLIENT
    GROK_CLIENT = GrokClient(history_msg_count=MESSAGE_HISTORY_COUNT)

    GROK_CLIENT.history.from_file()
    GROK_CLIENT.history.set_main_system_prompt(PERSONALITY)

    await bot.delete_webhook(drop_pending_updates=True)
    dp.include_router(router)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())