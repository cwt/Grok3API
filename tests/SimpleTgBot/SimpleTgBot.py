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
    logger.info('The .env file has been created. Fill in the required fields.')
    exit(1)

load_dotenv()
BOT_TOKEN = os.getenv('BOT_BOT_TOKEN', None) or exit(logger.error('BOT_BOT_TOKEN is not specified'))
ALLOWED_USER_IDS = [int(uid) for uid in os.getenv('BOT_ALLOWED_USER_IDS', '').split() if uid.strip()] or exit(logger.error('BOT_ALLOWED_USER_IDS is not specified'))
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
            logger.debug(f"Link to MD Viewer: {response.text}")
            return response.text
        else:
            logger.debug(f"Worker response error: {response.status_code}, {response.text}")
            return None
    except Exception as e:
        logger.error(f"Error uploading to Worker: {e}")
        return None

async def safe_target_reply(message: types.Message, text: str, parse_mode: str = None,
                            reply_to_message_id: int = None,
                            **kwargs):
    try:
        await message.answer(text, parse_mode=parse_mode, reply_to_message_id=reply_to_message_id, **kwargs)
    except exceptions.TelegramBadRequest as e:
        if "message to be replied not found" in e.message.lower():
            logger.warning(f"Message to reply to not found, sending without reply_to_message_id: {e}")
            await message.answer(text, parse_mode=parse_mode, **kwargs)
        raise e

async def reply_long_message(message: types.Message, text, max_length=4000):
    logger.debug(f"Sending message to chat {message.chat.id}, text length: {len(text)}")

    if not text.strip():
        logger.error("Attempting to send an empty message.")
        await safe_target_reply(message, "Error: empty message.", reply_to_message_id=message.message_id)
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

    logger.debug(f"Message split into {len(parts)} parts")

    for i, part in enumerate(parts):
        await send_with_fallback(message, part, worker_link, is_last=(i == len(parts) - 1))


async def send_with_fallback(message: types.Message, text: str, worker_link: str = None, is_last: bool = True):
    reply_markup = None
    link_text = f"\n\n[🌐 Response on MarkForge]({worker_link})" if worker_link and is_last else ""

    try:
        if worker_link and is_last:
            builder = InlineKeyboardBuilder()
            builder.button(text="📄 Open response", url=worker_link)
            reply_markup = builder.as_markup()

        await safe_target_reply(
            message, f"{text}{link_text}", parse_mode="Markdown",
            reply_to_message_id=message.message_id, reply_markup=reply_markup
        )
    except Exception as e:
        logger.debug(f"Error sending in Markdown: {e}")
        try:
            await safe_target_reply(
                message, link_text, parse_mode="Markdown",
                reply_to_message_id=message.message_id, reply_markup=reply_markup
            )
        except Exception as e:
            logger.error(f"Error sending in HTML: {e}")
            await safe_target_reply(message, text, reply_to_message_id=message.message_id)


async def send_md_view(message: types.Message, full_text, worker_link) -> bool:
    try:
        file_buffer = BytesIO(full_text.encode("utf-8"))
        file_buffer.name = "answer.md"

        link_text = f"[🌐 Response on MarkForge]({worker_link})" if worker_link else "📄 Response in file"

        builder = InlineKeyboardBuilder()
        builder.button(text="📄 Open response", url=worker_link)
        reply_markup = builder.as_markup() if worker_link else None

        if worker_link:
            await safe_target_reply(message, link_text, parse_mode="Markdown",
                                    reply_to_message_id=message.message_id, reply_markup=reply_markup)
        else:
            await message.answer_document(
                types.BufferedInputFile(file_buffer.read(), filename=file_buffer.name),
                caption="📄 Response in file", parse_mode="Markdown", reply_to_message_id=message.message_id
            )
            logger.debug(f"File {file_buffer.name} sent to user")
        return True
    except Exception as e:
        logger.error(f"Error in send_md_view: {e}")
        return False


@router.message(~F.text.startswith("/"))
async def handle_message(message: Message):
    """Handles incoming messages from authorized users."""
    if message.from_user.id not in ALLOWED_USER_IDS:
        logger.info(f"Ignoring message from user {message.from_user.id}")
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
    logger.info(f"Incoming from {sender}: {message.text or message.caption}")

    chat_id = str(message.chat.id)
    msg_text = await get_media_preview(message) or ""
    msg_text += message.text or message.caption or ""

    if not msg_text.strip():
        logger.error("Received an empty message.")
        await message.answer("Error: message is empty.")
        return

    try:
        await bot.send_chat_action(chat_id=message.chat.id, action="typing")
        logger.debug("Sent 'typing' action to chat")

        response = await GROK_CLIENT.async_ask(message=msg_text, history_id=chat_id)
        text_response = response.modelResponse.message if response.modelResponse else ""

        await reply_long_message(message, text_response)

        if response.modelResponse.generatedImages:
            logger.debug(f"Sending {len(response.modelResponse.generatedImages)} images")
            await bot.send_chat_action(chat_id=message.chat.id, action="upload_photo")
            media = []
            for img in response.modelResponse.generatedImages:
                image_file = await img.async_download()
                image_file.seek(0)
                media.append(InputMediaPhoto(media=BufferedInputFile(image_file.read(), filename="image.jpg")))

            await bot.send_media_group(chat_id=message.chat.id, media=media)
            logger.debug("Images sent")

        GROK_CLIENT.history.to_file()

    except Exception as e:
        logger.error(f"Error in handle_message: {e}")
        await message.answer("An error occurred while processing the request.")
        await bot.send_chat_action(chat_id=message.chat.id, action="cancel")
        logger.debug("Action canceled due to error")


@router.message(Command("clear"))
async def handle_clean_command(message: Message):
    """Handles the /clean command to clear chat history."""
    if message.from_user.id not in ALLOWED_USER_IDS:
        logger.info(f"Ignoring /clean command from user {message.from_user.id}")
        return

    logger.debug(f"Received /clean command from {message.from_user.id}")
    try:
        chat_id = str(message.chat.id)

        GROK_CLIENT.history.del_history_by_id(chat_id)
        GROK_CLIENT.history.to_file()
        GROK_CLIENT.history.from_file()

        logger.debug(f"History for chat {chat_id} deleted")

        GROK_CLIENT.history.to_file()
        logger.debug("History saved to file")
        await message.answer("History cleared.")
        logger.debug("Clearance response sent")

    except Exception as e:
        logger.error(f"In handle_clean_command: {e}")
        await message.answer("Failed to clear history.")
        logger.debug("Error message sent")


async def get_media_preview(message: Message) -> str:
    try:
        placeholders: List[str] = []
        if message.photo: placeholders.append("*Low-quality photo*\n")
        if message.animation: placeholders.append("*Low-quality animation*\n")
        if message.video: placeholders.append("*Low-quality video*\n")
        if message.video_note: placeholders.append("*Short low-quality video*\n")
        if message.sticker and message.sticker.thumbnail:
            placeholders.append(f"*Sticker: {message.sticker.emoji}*\n" if message.sticker.emoji
                              else "*Unknown sticker*\n")
        if message.audio: placeholders.append("*Low-quality audio file*\n")
        if message.voice: placeholders.append("*Low-quality voice message*\n")
        if message.document: placeholders.append("*Document, unable to preview*\n")
        if message.contact: placeholders.append("*Contact, data not displayed*\n")
        if message.location: placeholders.append("*Location, map unavailable*\n")
        if message.venue: placeholders.append("*Venue, information not displayed*\n")
        if message.poll: placeholders.append("*Poll, results not visible*\n")
        if message.dice: placeholders.append("*Dice, value not determined*\n")
        if message.game: placeholders.append("*Game, preview unavailable*\n")
        if message.invoice: placeholders.append("*Invoice, details not displayed*\n")
        if message.successful_payment: placeholders.append("*Successful payment, data hidden*\n")
        if message.passport_data: placeholders.append("*Passport data, information blocked*\n")
        if message.proximity_alert_triggered: placeholders.append("*Proximity alert, data unavailable*\n")
        if message.forum_topic_created: placeholders.append("*Forum topic created, details absent*\n")
        if message.forum_topic_edited: placeholders.append("*Forum topic edited, changes not visible*\n")
        if message.forum_topic_closed: placeholders.append("*Forum topic closed*\n")
        if message.forum_topic_reopened: placeholders.append("*Forum topic reopened*\n")
        if message.video_chat_scheduled: placeholders.append("*Video chat scheduled, time not specified*\n")
        if message.video_chat_started: placeholders.append("*Video chat started, access restricted*\n")
        if message.video_chat_ended: placeholders.append("*Video chat ended*\n")
        if message.video_chat_participants_invited: placeholders.append("*Video chat participants invited, list unavailable*\n")
        if message.web_app_data: placeholders.append("*Web app data, access closed*\n")
        if message.reply_markup: placeholders.append("*Inline keyboard, buttons not displayed*\n")
        return "".join(placeholders) if placeholders else ""
    except Exception as e:
        logger.error(f"In get_media_preview: {e}")
        return ""


async def main():
    """Main function to start the bot"""
    global GROK_CLIENT
    GROK_CLIENT = GrokClient(history_msg_count=MESSAGE_HISTORY_COUNT,
                             cookies="YOUR_BROWSER_COOKIES")

    GROK_CLIENT.history.set_main_system_prompt(PERSONALITY)

    await bot.delete_webhook(drop_pending_updates=True)
    dp.include_router(router)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
