import logging
import os

from telegram import Update
from telegram.ext import Application, ContextTypes, MessageHandler, filters

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
# Keep httpx quiet: its request logs include the bot token in the URL
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

# Configuration (read from environment variables, never hardcode secrets)
BOT_TOKEN = os.environ.get("BOT_TOKEN")
YOUR_CHAT_ID = os.environ.get("YOUR_CHAT_ID")

if not BOT_TOKEN or not YOUR_CHAT_ID:
    raise SystemExit(
        "Missing configuration: set the BOT_TOKEN and YOUR_CHAT_ID environment variables."
    )


def sender_label(update: Update) -> str:
    """Build a readable sender label, handling users without a username."""
    user = update.effective_user
    username = f"@{user.username}" if user.username else "no username"
    return f"{user.full_name} ({username}, id: {user.id})"


async def forward_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Forward any message received by the bot to your personal chat."""
    message = update.message
    if message is None:
        return

    try:
        sender = sender_label(update)
        caption_extra = f":\n{message.caption}" if message.caption else ""

        if message.text:
            await context.bot.send_message(
                chat_id=YOUR_CHAT_ID,
                text=f"📩 New message from {sender}:\n\n{message.text}",
            )
        elif message.photo:
            await context.bot.send_photo(
                chat_id=YOUR_CHAT_ID,
                photo=message.photo[-1].file_id,
                caption=f"📷 Photo from {sender}{caption_extra}",
            )
        elif message.document:
            await context.bot.send_document(
                chat_id=YOUR_CHAT_ID,
                document=message.document.file_id,
                caption=f"📎 Document from {sender}{caption_extra}",
            )
        elif message.voice:
            await context.bot.send_voice(
                chat_id=YOUR_CHAT_ID,
                voice=message.voice.file_id,
                caption=f"🎤 Voice message from {sender}",
            )
        elif message.video:
            await context.bot.send_video(
                chat_id=YOUR_CHAT_ID,
                video=message.video.file_id,
                caption=f"🎬 Video from {sender}{caption_extra}",
            )
        elif message.audio:
            await context.bot.send_audio(
                chat_id=YOUR_CHAT_ID,
                audio=message.audio.file_id,
                caption=f"🎵 Audio from {sender}{caption_extra}",
            )
        elif message.video_note:
            await context.bot.send_message(
                chat_id=YOUR_CHAT_ID, text=f"⭕ Video note from {sender}:"
            )
            await context.bot.send_video_note(
                chat_id=YOUR_CHAT_ID, video_note=message.video_note.file_id
            )
        elif message.sticker:
            await context.bot.send_message(
                chat_id=YOUR_CHAT_ID, text=f"🙂 Sticker from {sender}:"
            )
            await context.bot.send_sticker(
                chat_id=YOUR_CHAT_ID, sticker=message.sticker.file_id
            )
        else:
            # Unsupported type: tell the sender instead of pretending it worked
            await message.reply_text(
                "⚠️ Sorry, this type of message isn't supported. "
                "Please send text, a photo, a document, a voice message, or a video."
            )
            return

        # Confirmation to the sender (only for messages actually forwarded)
        await message.reply_text("✅ Your message has been received!")

    except Exception:
        logger.exception("Error forwarding message")
        await message.reply_text("❌ Sorry, there was an error processing your message.")


def main():
    """Start the bot."""
    application = Application.builder().token(BOT_TOKEN).build()

    # Handler for all non-command messages
    application.add_handler(
        MessageHandler(filters.ALL & ~filters.COMMAND, forward_message)
    )

    logger.info("Bot is starting...")
    application.run_polling()


if __name__ == "__main__":
    main()
