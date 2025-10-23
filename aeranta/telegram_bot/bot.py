import os
import django
import logging
import traceback
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext
from django.conf import settings
from .services import subscribe_user, unsubscribe_user
from .utils import decode_telegram_token
from .models import TelegramProfile


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'aeranta.settings')
django.setup()
logger = logging.getLogger(__name__)


def start(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    args = context.args or []

    if args:
        token = args[0]
        username = decode_telegram_token(token)
        if username:
            success = subscribe_user(chat_id, username)
            if success:
                update.message.reply_text("✅ You are now subscribed to Aeranta notifications!")
            else:
                update.message.reply_text("⚠️ User not found.")
        else:
            update.message.reply_text("⚠️ Invalid or expired token.")
    else:
        update.message.reply_text(
            "Welcome to Aeranta! Please start from the website to subscribe."
        )


def stop(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    logger.info("Received /stop from chat_id=%s", chat_id)
    print(f"[DEBUG] /stop called, chat_id={chat_id}")

    try:
        profile = TelegramProfile.objects.select_related('user').get(chat_id=chat_id)
        username = profile.user.username
    except TelegramProfile.DoesNotExist:
        update.message.reply_text("You are not currently subscribed.")
        return

    try:
        success = unsubscribe_user(username)
        if success:
            update.message.reply_text("🚫 You have been unsubscribed from Aeranta notifications.")
            logger.info("Unsubscribed username=%s", username)
        else:
            update.message.reply_text("⚠️ Could not unsubscribe.")
            logger.warning("Failed to unsubscribe username=%s", username)
    except Exception:
        traceback.print_exc()
        logger.exception("Exception in /stop handler")
        try:
            update.message.reply_text(
                "⚠️ Sorry, something went wrong while trying to unsubscribe."
            )
        except Exception:
            pass


def run_bot():
    """Запуск синхронного бота через polling"""
    token = settings.TELEGRAM_BOT_TOKEN
    updater = Updater(token=token, use_context=True)
    dispatcher = updater.dispatcher

    # Регистрируем команды
    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(CommandHandler('stop', stop))

    print("Telegram bot is running (polling)...")
    updater.start_polling()
    updater.idle()


def set_webhook():

    token = settings.TELEGRAM_BOT_TOKEN
    updater = Updater(token=token, use_context=True)
    url_path = token
    webhook_url = f"https://aeranta.net/telegram_bot/webhook/{url_path}/"
    updater.bot.set_webhook(url=webhook_url)

    print(f"Webhook set to: {webhook_url}")

