from celery import shared_task
from notifications.services import send_scheduled_notifications


@shared_task
def run_email_sending():
    send_scheduled_notifications()
