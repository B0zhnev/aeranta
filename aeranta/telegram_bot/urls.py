from django.conf import settings
from django.urls import path
from . import views

urlpatterns = [
    path(f'webhook/{settings.TELEGRAM_BOT_TOKEN}/', views.webhook, name='telegram_webhook'),
]