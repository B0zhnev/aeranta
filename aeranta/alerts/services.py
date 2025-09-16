from alerts.alerts import WindSpeedAlert, BabushkaAlert, IcyRoadAlert, AuroraAlert, DedushkaAlert, LunarAlert
from alerts.models import Alert
from notifications.services import send_notification
from django.utils import timezone

ALERT_CLASSES = {
    'wind_alert': WindSpeedAlert,
    'babushka': BabushkaAlert,
    'icy_road': IcyRoadAlert,
    'aurora_alert': AuroraAlert,
    'dedushka': DedushkaAlert,
    'lunar': LunarAlert
}

def run_alert_for_user(user, alert_slug):
    alert_obj = ALERT_CLASSES.get(alert_slug)
    if not alert_obj:
        return None
    instance = alert_obj(user)


def run_alert_for_user(user, alert_slug=None):
    try:
        alert_obj = Alert.objects.get(slug=alert_slug)
    except Alert.DoesNotExist:
        return None
    alert_class = ALERT_CLASSES.get(alert_obj.slug)
    if not alert_class:
        return None
    alert_instance = alert_class(user)
    result = alert_instance.check()
    print(f"{alert_slug} checked for {user}. Result: {'Triggered' if result else 'No alert'}")
    return result


def collector():
    now = timezone.now()
    for slug, alert_class in ALERT_CLASSES.items():
        try:
            alert_model = Alert.objects.get(slug=slug)
        except Alert.DoesNotExist as e:
            print(f'collector error - {e}')
            continue

        elapsed = (now - alert_model.last_checked).total_seconds()
        print(f'{elapsed} - {now - alert_model.last_checked} - sec{(now - alert_model.last_checked).total_seconds()}')
        if elapsed < alert_model.check_interval:
            continue

        users = alert_model.users.all()
        for user in users:
            answer = run_alert_for_user(user, slug)
            if answer:
                print(f'collector got message for {user}')
                send_notification(
                    user=user,
                    sender=answer[0],
                    message=answer[1],
                    local_date=answer[2],
                    local_time=answer[3],
                )

        alert_model.last_checked = now
        alert_model.save(update_fields=['last_checked'])
