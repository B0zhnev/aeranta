from django.contrib.auth import get_user_model
from django.template.loader import render_to_string
from .models import Notification
from django.utils import timezone
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from telegram_bot.utils import send_telegram_message

User = get_user_model()


def send_notification(user, message, sender, local_date, local_time):
    max_nots = 15
    user_nots = Notification.objects.filter(user=user)
    if user_nots.count() >= max_nots:
        Notification.objects.filter(user=user).last().delete()
    if Notification.objects.filter(user=user, message=message, local_date=local_date).exists():
        return
    Notification.objects.create(
        user=user,
        sender=sender,
        message=message,
        local_date=local_date,
        local_time=local_time
    )
    telegram_message = f'{sender}: {message}'
    send_telegram_message(user, telegram_message)


def update_email_nots_from_weather(user, user_selected_hour):
    if user_selected_hour == 0:
        user.email_nots = 0
        user.save(update_fields=['email_nots'])
        return

    user_hour = 0 if user_selected_hour == 24 else user_selected_hour

    try:
        tz_offset_sec = user.open_weather.timezone
        tz_offset_hours = tz_offset_sec // 3600
        server_hour = (user_hour - tz_offset_hours) % 24
        user.email_nots = 24 if server_hour == 0 else server_hour
        user.save(update_fields=['email_nots'])

    except user.openweatherapi.RelatedObjectDoesNotExist:
        user.email_nots = user_selected_hour
        user.save(update_fields=['email_nots'])


def send_scheduled_notifications():
    current_hour = timezone.now().hour
    if current_hour == 0:
        current_hour = 24

    users = User.objects.filter(email_nots=current_hour)
    for user in users:
        unread_notifications = user.notifications.filter(is_read=False, is_sent=False)
        if not unread_notifications.exists():
            continue

        context = {
            'user': user,
            'notifications': unread_notifications,
        }

        text_content = render_to_string('notifications/email_notifications.txt', context)
        html_content = render_to_string('notifications/email_notifications.html', context)

        email = EmailMultiAlternatives(
            subject='You have unread notifications',
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[user.email],
        )
        email.attach_alternative(html_content, "text/html")
        email.send(fail_silently=False)
        unread_notifications.update(is_sent=True)
        print(f'email sent for {user}')

