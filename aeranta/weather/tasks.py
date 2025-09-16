from celery import shared_task
from .services.ipgastronomy import auto_update_ipgastronomy
from .services.auroraslive import auto_update_auroras
from .services.openweather import auto_update_openweather


@shared_task
def run_auto_update_openweather():
    auto_update_openweather()


@shared_task
def run_auto_update_auroras():
    auto_update_auroras()


@shared_task
def run_auto_update_ipgastronomy():
    auto_update_ipgastronomy()