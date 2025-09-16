from django.utils.html import format_html_join
from django.utils.safestring import mark_safe
from django.contrib import admin
from alerts.models import Checker
from users.models import User


@admin.register(User)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'display_alerts', 'display_checkers')

    def display_alerts(self, obj):
        alerts = obj.alerts.all()
        if not alerts:
            return '-'
        return format_html_join(
            mark_safe('<br>'),
            '{}',
            ((alert.name,) for alert in alerts)
        )
    display_alerts.short_description = 'Подписки (Alerts)'

    def display_checkers(self, obj):
        checkers = Checker.objects.filter(alert__in=obj.alerts.all()).distinct()
        if not checkers:
            return '-'
        return format_html_join(
            mark_safe('<br>'),
            '{}',
            ((checker.parameter_name,) for checker in checkers)
        )
    display_checkers.short_description = 'Users checkers'