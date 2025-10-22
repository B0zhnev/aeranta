import base64
import hmac
import hashlib
import json
from django.conf import settings
from telegram import Bot
from telegram.error import TelegramError
from .models import TelegramProfile
import asyncio

bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)


def encode_payload(payload_dict):
    """Кодирует словарь в безопасный base64"""
    json_bytes = json.dumps(payload_dict, separators=(',', ':')).encode()
    return base64.urlsafe_b64encode(json_bytes).decode()


def decode_payload(encoded_payload):
    """Декодирует base64 обратно в словарь"""
    try:
        json_bytes = base64.urlsafe_b64decode(encoded_payload.encode())
        return json.loads(json_bytes)
    except Exception:
        return None


def generate_telegram_token(username):
    """Генерирует токен для username любого вида"""
    payload = {'username': username}
    payload_b64 = encode_payload(payload)

    signature = hmac.new(
        settings.SECRET_KEY.encode(),
        payload_b64.encode(),
        hashlib.sha256
    ).digest()
    signature_b64 = base64.urlsafe_b64encode(signature).decode()

    return f"{payload_b64}.{signature_b64}"


def decode_telegram_token(token):
    """Декодирует токен и проверяет подпись"""
    try:
        payload_b64, signature_b64 = token.rsplit('.', 1)
        payload = decode_payload(payload_b64)
        if not payload or 'username' not in payload:
            return None

        expected_signature = hmac.new(
            settings.SECRET_KEY.encode(),
            payload_b64.encode(),
            hashlib.sha256
        ).digest()
        if hmac.compare_digest(base64.urlsafe_b64decode(signature_b64.encode()), expected_signature):
            return payload['username']
        return None
    except Exception:
        return None


def send_telegram_message(user, message):
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
