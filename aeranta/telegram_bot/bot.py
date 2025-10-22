import os
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from asgiref.sync import sync_to_async
from django.conf import settings
from .services import subscribe_user, unsubscribe_user
from .utils import decode_telegram_token
from .models import TelegramProfile
import logging
import traceback

logger = logging.getLogger(__name__)

# Обертка
async_subscribe_user = sync_to_async(subscribe_user, thread_sensitive=True)
async_unsubscribe_user = sync_to_async(unsubscribe_user, thread_sensitive=True)


async_get_profile = sync_to_async(
    lambda chat_id: TelegramProfile.objects.select_related('user').get(chat_id=chat_id),
    thread_sensitive=True
)


# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    args = context.args or []

    if args:
        token = args[0]
        username = decode_telegram_token(token)
        if username:
            success = await async_subscribe_user(chat_id, username)
            if success:
                await update.message.reply_text(
                    "✅ You are now subscribed to Aeranta notifications!"
                )
            else:
                await update.message.reply_text("⚠️ User not found.")
        else:
            await update.message.reply_text("⚠️ Invalid or expired token.")
    else:
        await update.message.reply_text(
            "Welcome to Aeranta! Please start from the website to subscribe."
        )


# /stop
async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Отписывает пользователя по chat_id через username.
    """
    try:
        chat_id = update.effective_chat.id
        logger.info("Received /stop from chat_id=%s", chat_id)
        print(f"[DEBUG] /stop called, chat_id={chat_id}")

        # получаем профиль по chat_id
        try:
            profile = await async_get_profile(str(chat_id))
            username = profile.user.username
        except TelegramProfile.DoesNotExist:
            await update.message.reply_text("You are not currently subscribed.")
            return

        # вызываем существующую функцию отписки
        success = await async_unsubscribe_user(username)
        if success:
            await update.message.reply_text(
                "🚫 You have been unsubscribed from Aeranta notifications."
            )
            logger.info("Unsubscribed username=%s", username)
        else:
            await update.message.reply_text("⚠️ Could not unsubscribe.")
            logger.warning("Failed to unsubscribe username=%s", username)

    except Exception as exc:
        traceback.print_exc()
        logger.exception("Exception in /stop handler")
        try:
            await update.message.reply_text(
                "⚠️ Sorry, something went wrong while trying to unsubscribe."
            )
        except Exception:
            pass


# Инициализация
def run_bot():
    """Запуск бота в режиме polling (для отладки)"""
    token = settings.TELEGRAM_BOT_TOKEN
    application = Application.builder().token(token).build()

    # Регистрируем команды
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('stop', stop))

    print("Telegram bot is running (polling)...")
    application.run_polling()


# Webhook setup
def set_webhook():
    """Устанавливает webhook на прод"""
    token = settings.TELEGRAM_BOT_TOKEN
    app = Application.builder().token(token).build()

    webhook_url = f"https://aeranta.net/telegram_bot/webhook/"

    async def _set():
        await app.bot.set_webhook(webhook_url)
        print(f"Webhook set to: {webhook_url}")

    # Запускаем установку в event loop
    import asyncio
    asyncio.run(_set())
