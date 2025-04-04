import asyncio
from typing import List
import logging
from logging.handlers import RotatingFileHandler
import os
from io import BytesIO

import requests
from aiogram.utils.keyboard import InlineKeyboardBuilder
from dotenv import load_dotenv

from aiogram import Bot, Dispatcher, types, exceptions
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, BufferedInputFile, InputMediaPhoto
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
                     'BOT_MESSAGE_HISTORY_COUNT=10\n', 'BOT_PERSONALITY=\n',
                      'WORKER_URL=\n'])
    logger.info('Файл .env создан. Заполните необходимые поля.')
    exit(1)

load_dotenv()
BOT_TOKEN = os.getenv('BOT_BOT_TOKEN', None) or exit(logger.error('BOT_BOT_TOKEN не указан'))
ALLOWED_USER_IDS = [int(uid) for uid in os.getenv('BOT_ALLOWED_USER_IDS', '').split() if uid.strip()] or exit(logger.error('BOT_ALLOWED_USER_IDS не указан'))
MESSAGE_HISTORY_COUNT = int(os.getenv('BOT_MESSAGE_HISTORY_COUNT', 10))
PERSONALITY = os.getenv('BOT_PERSONALITY', '')
WORKER_URL = os.getenv('WORKER_URL', '')

GROK_CLIENT: GrokClient
bot = Bot(token=BOT_TOKEN)
router = Router()
dp = Dispatcher()


async def upload_to_worker(text):
    try:
        response = requests.post(WORKER_URL, data=text)
        if response.status_code == 200 and response.text.startswith("https://"):
            logger.debug(f"Ссылка на MD Viewer: {response.text}")
            return response.text
        else:
            logger.debug(f"Ошибка ответа от Worker: {response.status_code}, {response.text}")
            return None
    except Exception as e:
        logger.error(f"Ошибка при загрузке на Worker: {e}")
        return None

async def safe_target_reply(message: types.Message, text: str, parse_mode: str = None,
                            reply_to_message_id: int = None,
                            **kwargs):
    try:
        await message.answer(text, parse_mode=parse_mode, reply_to_message_id=reply_to_message_id, **kwargs)
    except exceptions.TelegramBadRequest as e:
        if "message to be replied not found" in e.message.lower():
            logger.warning(f"Сообщение для ответа не найдено, отправка без reply_to_message_id: {e}")
            await message.answer(text, parse_mode=parse_mode, **kwargs)
        raise e

async def reply_long_message(message: types.Message, text, max_length=4000):
    logger.debug(f"Отправка сообщения в чат {message.chat.id}, длина текста: {len(text)}")

    if not text.strip():
        logger.error("Попытка отправить пустое сообщение.")
        await safe_target_reply(message, "Ошибка: пустое сообщение.", reply_to_message_id=message.message_id)
        return

    worker_link = None
    if WORKER_URL:
        if len(text) > max_length or any(char in text for char in ("#", "*", "`")):
            worker_link = await upload_to_worker(text)

    if len(text) <= max_length:
        await send_with_fallback(message, text, worker_link)
        return

    if await send_md_view(message, text, worker_link):
        return

    parts = []
    while text:
        if len(text) <= max_length:
            parts.append(text)
            break
        split_pos = text.rfind(' ', 0, max_length)
        if split_pos == -1:
            split_pos = max_length
        parts.append(text[:split_pos])
        text = text[split_pos:].lstrip()

    logger.debug(f"Сообщение разбито на {len(parts)} частей")

    for i, part in enumerate(parts):
        await send_with_fallback(message, part, worker_link, is_last=(i == len(parts) - 1))


async def send_with_fallback(message: types.Message, text: str, worker_link: str = None, is_last: bool = True):
    reply_markup = None
    link_text = f"\n\n[🌐 Ответ на MarkForge]({worker_link})" if worker_link and is_last else ""

    try:
        if worker_link and is_last:
            builder = InlineKeyboardBuilder()
            builder.button(text="📄 Открыть ответ", url=worker_link)
            reply_markup = builder.as_markup()

        await safe_target_reply(
            message, f"{text}{link_text}", parse_mode="Markdown",
            reply_to_message_id=message.message_id, reply_markup=reply_markup
        )
    except Exception as e:
        logger.debug(f"Ошибка при отправке в Markdown: {e}")
        try:
            await safe_target_reply(
                message, link_text, parse_mode="Markdown",
                reply_to_message_id=message.message_id, reply_markup=reply_markup
            )
        except Exception as e:
            logger.error(f"Ошибка при отправке в HTML: {e}")
            await safe_target_reply(message, text, reply_to_message_id=message.message_id)


async def send_md_view(message: types.Message, full_text, worker_link) -> bool:
    try:
        file_buffer = BytesIO(full_text.encode("utf-8"))
        file_buffer.name = "answer.md"

        link_text = f"[🌐 Ответ на MarkForge]({worker_link})" if worker_link else "📄 Ответ в файле"

        builder = InlineKeyboardBuilder()
        builder.button(text="📄 Открыть ответ", url=worker_link)
        reply_markup = builder.as_markup() if worker_link else None

        if worker_link:
            await safe_target_reply(message, link_text, parse_mode="Markdown",
                                    reply_to_message_id=message.message_id, reply_markup=reply_markup)
        else:
            await message.answer_document(
                types.BufferedInputFile(file_buffer.read(), filename=file_buffer.name),
                caption="📄 Ответ в файле", parse_mode="Markdown", reply_to_message_id=message.message_id
            )
            logger.debug(f"Файл {file_buffer.name} отправлен пользователю")
        return True
    except Exception as e:
        logger.error(f"Ошибка в send_md_view: {e}")
        return False



@router.message(~F.text.startswith("/"))
async def handle_message(message: Message):
    """Обрабатывает входящие сообщения от разрешенных пользователей."""
    if message.from_user.id not in ALLOWED_USER_IDS:
        logger.info(f"Игнорирую сообщение от пользователя {message.from_user.id}")
        return
    if message and message.from_user:
        if message.from_user.username:
            sender = "@" + message.from_user.username
        else:
            sender_first_name = message.from_user.first_name or ""
            sender_last_name = message.from_user.last_name or ""
            sender = sender_first_name + " " + sender_last_name
            if sender.strip() == "" or sender.isspace():
                sender = message.from_user.id
    else:
        sender = message.chat.id
    logger.info(f"Входящее от {sender}: {message.text or message.caption}")

    chat_id = str(message.chat.id)
    msg_text = await get_media_preview(message) or ""
    msg_text += message.text or message.caption or ""

    if not msg_text.strip():
        logger.error("Получено пустое сообщение.")
        await message.answer("Ошибка: сообщение пустое.")
        return

    try:
        await bot.send_chat_action(chat_id=message.chat.id, action="typing")
        logger.debug("Отправлено действие 'typing' в чат")

        response = await GROK_CLIENT.async_ask(message=msg_text, history_id=chat_id)
        text_response = response.modelResponse.message if response.modelResponse else ""

        await reply_long_message(message, text_response)

        if response.modelResponse.generatedImages:
            logger.debug(f"Отправка {len(response.modelResponse.generatedImages)} изображений")
            await bot.send_chat_action(chat_id=message.chat.id, action="upload_photo")
            media = []
            for img in response.modelResponse.generatedImages:
                image_file = await img.async_download()
                image_file.seek(0)
                media.append(InputMediaPhoto(media=BufferedInputFile(image_file.read(), filename="image.jpg")))

            await bot.send_media_group(chat_id=message.chat.id, media=media)
            logger.debug("Изображения отправлены")

        GROK_CLIENT.history.to_file()

    except Exception as e:
        logger.error(f"Ошибка в handle_message: {e}")
        await message.answer("Произошла ошибка при обработке запроса.")
        await bot.send_chat_action(chat_id=message.chat.id, action="cancel")
        logger.debug("Действие отменено из-за ошибки")

@router.message(Command("clear"))
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
    GROK_CLIENT = GrokClient(history_msg_count=MESSAGE_HISTORY_COUNT,
                             cookies="YOUR_BROWSER_COOKIES")

    GROK_CLIENT.history.set_main_system_prompt(PERSONALITY)

    await bot.delete_webhook(drop_pending_updates=True)
    dp.include_router(router)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())