import json
from django.http import HttpResponse, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from telegram import Update, Bot
from telegram.ext import Dispatcher, CommandHandler
from .bot import start, stop

bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
dispatcher = Dispatcher(bot, None, workers=0)
dispatcher.add_handler(CommandHandler('start', start))
dispatcher.add_handler(CommandHandler('stop', stop))


@csrf_exempt
def webhook(request):
    if request.method != "POST":
        return HttpResponseForbidden("Invalid method")
    try:
        payload = json.loads(request.body.decode("utf-8"))
    except Exception:
        return HttpResponseForbidden("Invalid payload")
    update = Update.de_json(payload, bot)
    dispatcher.process_update(update)
    return HttpResponse("OK")