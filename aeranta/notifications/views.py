from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views import View
from django.views.generic import ListView
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from telegram_bot.services import unsubscribe_user
from .forms import EmailNotificationForm
from .services import update_email_nots_from_weather
from notifications.models import Notification
from django.views.decorators.cache import never_cache
from telegram_bot.utils import generate_telegram_token


class NotificationListView(LoginRequiredMixin, ListView):
    model = Notification
    template_name = 'notifications/list.html'
    context_object_name = 'notifications'

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        notifications = context['notifications']

        processed_notifications = []
        has_unread = any(not n.is_read for n in notifications)

        for idx, n in enumerate(notifications):
            if n.is_read:
                opacity = 1.0 - (idx / 14) * 1.05
            else:
                opacity = 1.0
            processed_notifications.append({
                'notification': n,
                'opacity': round(opacity, 2)
            })
        context['notifications'] = processed_notifications
        context['has_unread'] = has_unread
        return context


class MarkReadView(LoginRequiredMixin, View):
    def post(self, request, pk):
        n = get_object_or_404(Notification, pk=pk, user=request.user)
        if not n.is_read:
            n.is_read = True
            n.save()
        next_url = request.POST.get('next') or request.Meta.get('HTTP_REFERER') or reverse('notifications:list')
        return redirect(next_url)


class AllMarkReadView(LoginRequiredMixin, View):
    def post(self, request):
        request.user.notifications.filter(is_read=False).update(is_read=True)
        next_url = request.POST.get('next') or request.Meta.get('HTTP_REFERER') or reverse('notifications:list')
        return redirect(next_url)


@never_cache
@login_required
def edit_email_notifications(request):
    user = request.user
    if not getattr(user, 'email_confirmed', False):
        return render(request, 'notifications/email_not_confirmed.html')

    if request.method == 'POST':
        form = EmailNotificationForm(request.POST, instance=user)
        if form.is_valid():
            user = form.save(commit=False)
            user.save()
            update_email_nots_from_weather(user, user_selected_hour=int(form.cleaned_data['email_nots']))
            return redirect('notifications:list')
    else:
        form = EmailNotificationForm(instance=user)
    
    try:
        tz_offset_hours = user.open_weather.timezone // 3600
        if user.email_nots == 0:
            local_email_hour = 0
        else:
            local_email_hour = (user.email_nots + tz_offset_hours) % 24
    except:
        local_email_hour = user.email_nots
    
    data = {'form': form, 'local_email_hour': local_email_hour}
    
    return render(request, 'notifications/edit_email_notifications.html', context=data)


def telegram_notifications(request):
    username = request.user.username
    link = f'https://t.me/AerantaBot?start={generate_telegram_token(username)}'
    return render(request, 'notifications/telegram_notifications.html', {'link':link})


@login_required
def telegram_unsubscribe(request):
    success = unsubscribe_user(request.user.username)
    if success:
        messages.success(request, 'You have successfully unsubscribed from Telegram notifications.')
    else:
        messages.warning(request, 'No active Telegram subscription found.')

    return redirect('notifications:telegram_notifications')