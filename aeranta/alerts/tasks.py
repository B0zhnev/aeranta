from celery import shared_task
from .services import collector


@shared_task
def run_collector():
    collector()

