CELERY_BEAT_SCHEDULE = {
    'run-collector-every-15-minutes': {
        'task': 'alerts.tasks.run_collector',
        'schedule': 15.0,
    },
    'run-openweather-update-every-30-minutes': {
        'task': 'weather.tasks.run_auto_update_openweather',
        'schedule': 30.0,
    },
}