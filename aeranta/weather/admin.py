from django.contrib import admin
from django.utils.html import format_html_join, mark_safe
from alerts.models import Checker
from .models import OpenWeatherApi


@admin.register(OpenWeatherApi)
class OpenWeatherApiAdmin(admin.ModelAdmin):
    list_display = ('user', 'list_alerts', 'list_checkers')

    def list_alerts(self, obj):
        # Получаем подписки пользователя (Alert)
        alerts = obj.user.alerts.all()  # или .alert_set.all(), смотря как related_name
        if not alerts:
            return '-'
        return format_html_join(
            mark_safe('<br>'),
            '{}',
            ((alert.name,) for alert in alerts)
        )
    list_alerts.short_description = 'Подписки пользователя'

    def list_checkers(self, obj):
        # Все чекеры из подписок пользователя
        alerts = obj.user.alerts.all()
        checkers = Checker.objects.filter(alert__in=alerts).distinct()
        if not checkers:
            return '-'
        return format_html_join(
            mark_safe('<br>'),
            '{}',
            ((checker.parameter_name,) for checker in checkers)
        )
    list_checkers.short_description = 'Чекеры подписок пользователя'