from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.views import View
from django.views.generic import ListView
from alerts.models import Alert, Checker
from weather.models import OpenWeatherApi



class AlertListView(LoginRequiredMixin, ListView):
    model = Alert
    template_name = 'alerts/alert_list.html'
    context_object_name = 'alerts'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['subscribed_ids'] = set(self.request.user.alerts.values_list('id', flat=True))
        return ctx


class ToggleAlertSubscriptionView(LoginRequiredMixin, View):
    def post(self, request, slug):
        alert = get_object_or_404(Alert, slug=slug)
        user = request.user

        if user in alert.users.all():
            alert.users.remove(user)

            for checker in alert.checkers.all():
                api_model = checker.api.model_class()
                api_ct = checker.api
                has_checkers = Checker.objects.filter(
                    api=api_ct,
                    alert__users=user
                ).exists()
                if not has_checkers and api_model != OpenWeatherApi:
                    api_model.objects.filter(user=user).delete()
        else:
            alert.users.add(user)
            for checker in alert.checkers.all():
                api_model = checker.api.model_class()
                api_model.objects.get_or_create(user=user)
        return redirect(reverse('alerts:list'))


