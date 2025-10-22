import base64
import hmac
import hashlib
from django.conf import settings
from telegram import Bot
from telegram.error import TelegramError
from .models import TelegramProfile
import asyncio

bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)


def generate_telegram_token(user_id: int) -> str:
    """
    Генерирует токен для Telegram по ID пользователя.
    """
    secret = settings.SECRET_KEY.encode()
    user_bytes = str(user_id).encode()
    signature = hmac.new(secret, user_bytes, hashlib.sha256).digest()

    user_b64 = base64.urlsafe_b64encode(user_bytes).decode()
    signature_b64 = base64.urlsafe_b64encode(signature).decode()

    token = base64.urlsafe_b64encode(f'{user_b64}:{signature_b64}'.encode()).decode()
    return token


def decode_telegram_token(token: str) -> int | None:
    """
    Декодирует токен и возвращает ID пользователя, если подпись верна.
    """
    try:
        decoded = base64.urlsafe_b64decode(token.encode()).decode()
        user_b64, signature_b64 = decoded.split(':', 1)

        user_bytes = base64.urlsafe_b64decode(user_b64.encode())
        signature = base64.urlsafe_b64decode(signature_b64.encode())

        expected_signature = hmac.new(
            settings.SECRET_KEY.encode(),
            user_bytes,
            hashlib.sha256
        ).digest()

        if hmac.compare_digest(signature, expected_signature):
            return int(user_bytes.decode())
        return None
    except Exception:
        return None


def send_telegram_message(user, message):
    """
    Отправляет сообщение в Telegram, если профиль активен.
    """
    try:
        profile = TelegramProfile.objects.get(user=user, is_active=True)
    except TelegramProfile.DoesNotExist:
        return False

    async def _send():
        try:
            await bot.send_message(chat_id=profile.chat_id, text=message)
            return True
        except TelegramError as e:
            print(f'TelegramError: {e}')
            return False

    return asyncio.run(_send())