from .models import TelegramProfile
from django.contrib.auth import get_user_model

User = get_user_model()


def subscribe_user(chat_id, username):
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        return False

    profile, created = TelegramProfile.objects.update_or_create(
        user=user,
        defaults={'chat_id': chat_id, 'is_active': True}
    )
    return True


def unsubscribe_user(username):
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        return False
    deleted, _ = TelegramProfile.objects.filter(user=user).delete()
    return deleted > 0