from django.shortcuts import render

# Create your views here.
import json
import logging
import traceback
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from telegram import Update
from telegram.ext import Application, CommandHandler
from django.conf import settings

from .bot import start, stop

logger = logging.getLogger(__name__)

# Инициализация приложения Telegram для webhook
application = Application.builder().token(settings.TELEGRAM_BOT_TOKEN).build()
application.add_handler(CommandHandler('start', start))
application.add_handler(CommandHandler('stop', stop))


@csrf_exempt
def webhook(request):
    """
    View для приема POST-запросов от Telegram.
    Telegram будет слать сюда обновления пользователей.
    """
    if request.method != "POST":
        return JsonResponse({"ok": False, "error": "Only POST allowed"}, status=400)

    try:
        data = json.loads(request.body)
        update = Update.de_json(data, application.bot)

        # Отправляем update в очередь dispatcher для обработки
        application.update_queue.put(update)

        return JsonResponse({"ok": True})

    except Exception as exc:
        logger.exception("Error processing Telegram webhook update")
        traceback.print_exc()
        return JsonResponse({"ok": False, "error": str(exc)}, status=500)