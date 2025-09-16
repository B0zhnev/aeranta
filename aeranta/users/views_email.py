from django.contrib.auth.forms import SetPasswordForm
from django.contrib.auth.views import PasswordResetView, PasswordResetConfirmView
from django.urls import reverse_lazy
from django.shortcuts import render, redirect
from .forms import ConfirmedEmailPasswordResetForm
from .models import User
from .utils import read_email_token
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .utils import send_email_confirmation


@login_required
def send_confirmation_email_view(request):
    if request.method == 'POST':
        user = request.user
        if user.email:
            send_email_confirmation(request, user, user.email)
            messages.success(request, 'Confirmation email has been sent to your address.')
        else:
            messages.error(request, 'You don’t have an email set.')
    return redirect('notifications:edit_email_notifications')


class ConfirmedEmailPasswordResetView(PasswordResetView):
    form_class = ConfirmedEmailPasswordResetForm
    template_name = 'users/password_reset_form.html'
    email_template_name = 'users/password_reset_email.html'
    html_email_template_name = 'users/password_reset_email.html'
    subject_template_name = 'users/password_reset_subject.txt'
    success_url = '/users/password-reset/done/'


class PasswordResetCf(PasswordResetConfirmView):
    template_name = 'users/password_reset_confirm.html'
    form_class = SetPasswordForm
    success_url = reverse_lazy("users:password_reset_complete")


@login_required
def confirm_email_prompt(request):
    """
    Страница подтверждения email после регистрации.
    Редактируемое поле email, кнопки Confirm и Skip.
    """
    user = request.user

    if request.method == 'POST':
        target_email = request.POST.get('email', '').strip()

        if not target_email:
            messages.error(request, 'Please provide a valid email.')
            return redirect('users:confirm_email_prompt')

        # Проверяем, не занят ли email другим пользователем
        if User.objects.filter(email=target_email).exclude(pk=user.pk).exists():
            messages.error(request, 'This email is already used by another account.')
            return redirect('users:confirm_email_prompt')

        # Сохраняем в pending_email, не трогаем основной email до подтверждения
        user.pending_email = target_email
        user.save(update_fields=['pending_email'])

        # Отправляем письмо с токеном на pending_email
        try:
            send_email_confirmation(request, user, target_email)
        except Exception as e:
            # лучше логировать: import logging; logger.exception(...)
            messages.error(request, 'Failed to send confirmation email. Please try again later.')
            return redirect('users:confirm_email_prompt')

        # Редирект на страницу с сообщением "instructions sent"
        return redirect('users:confirm_email_instructions_sent')

    # GET-запрос — показываем страницу с текущим email
    initial_email = user.pending_email or user.email or ''
    return render(request, 'users/confirm_email_prompt.html', {'email': initial_email})


@login_required
def confirm_email_skip(request):
    return redirect('users:post_registration')


@login_required
def confirm_email_instructions_sent(request):
    return render(request, 'users/confirm_email_instructions_sent.html')


@login_required
def post_registration(request):
    return render(request, 'users/post_registration.html')


def confirm_email_token_view(request, token):
    """
    Обработчик ссылки из письма подтверждения.
    - проверяет токен,
    - если токен валиден и email совпадает с user.pending_email -> переносит pending_email -> email и ставит email_confirmed=True
    - если токен валиден и email совпадает с user.email -> просто ставит email_confirmed=True
    - в остальных случаях показывает ошибку
    После успешного подтверждения редиректит на post_registration.
    """
    try:
        data = read_email_token(token)  # может бросить исключение при просрочке/некорректности
    except Exception:
        messages.error(request, 'Invalid or expired confirmation link.')
        # Возвращаем на страницу prompt, чтобы пользователь мог запросить письмо повторно
        return redirect('users:confirm_email_prompt')

    try:
        user = User.objects.get(pk=data['uid'])
    except User.DoesNotExist:
        messages.error(request, 'User for this confirmation link does not exist.')
        return redirect('users:confirm_email_prompt')

    confirmed_email = data.get('email')

    # Если pending_email совпадает с тем, что в токене — это ожидаемый сценарий
    if user.pending_email and user.pending_email == confirmed_email:
        user.email = confirmed_email
        user.pending_email = ''
        user.email_confirmed = True
        user.save(update_fields=['email', 'pending_email', 'email_confirmed'])
        messages.success(request, 'Your email has been confirmed successfully.')
        return redirect('users:post_registration')

    # Если pending_email не установлен, но токен совпадает с текущим email — просто подтверждаем
    if user.email and user.email == confirmed_email:
        if not user.email_confirmed:
            user.email_confirmed = True
            user.save(update_fields=['email_confirmed'])
        messages.success(request, 'Your email has been confirmed successfully.')
        return redirect('users:post_registration')

    # Иначе — токен валиден, но не соответствует ни pending_email, ни текущему email
    messages.error(request, 'This confirmation link does not match any pending email for this account.')
    return redirect('users:confirm_email_prompt')