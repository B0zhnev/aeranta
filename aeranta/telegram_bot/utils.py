import base64
import hmac
import hashlib
from django.conf import settings
from telegram import Bot
from telegram.error import TelegramError
from .models import TelegramProfile

bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)


def decode_telegram_token(token):
    try:
        decoded = base64.urlsafe_b64decode(token.encode())
        username_bytes, signature = decoded.rsplit(b'.', 1)
        username = username_bytes.decode()

        expected_signature = hmac.new(
            settings.SECRET_KEY.encode(),
            username_bytes,
            hashlib.sha256
        ).digest()

        if hmac.compare_digest(signature, expected_signature):
            return username
        return None
    except Exception:
        return None


def generate_telegram_token(username):
    secret = settings.SECRET_KEY.encode()
    username_bytes = username.encode()
    signature = hmac.new(secret, username_bytes, hashlib.sha256).digest()
    token = base64.urlsafe_b64encode(username_bytes + b"." + signature).decode()
    return token


def send_telegram_message(user, message):
    try:
        profile = TelegramProfile.objects.get(user=user, is_active=True)
    except TelegramProfile.DoesNotExist:
        return False

    try:
        bot.send_message(chat_id=profile.chat_id, text=message)
        return True
    except TelegramError as e:
        print(f'TelegramError: {e}')
        return False