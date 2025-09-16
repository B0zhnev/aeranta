from django.core import signing
from django.conf import settings
from django.urls import reverse
from django.core.mail import EmailMultiAlternatives


SIGN_SALT = 'email-confirm'
TOKEN_MAX_AGE = 3600 * 48


def make_email_token(user_id, email):
    return signing.dumps({'uid': user_id, 'email':email}, salt=SIGN_SALT)


def read_email_token(token):
    return signing.loads(token, salt=SIGN_SALT, max_age=TOKEN_MAX_AGE)


def send_email_confirmation(request, user, target_email):
    token = make_email_token(user.id, target_email)
    url = request.build_absolute_uri(reverse('users:confirm_email', kwargs={'token': token}))

    subject = 'Confirm your email'
    name = user.first_name if user.first_name else user.username
    html_content = f"""
        <p>Hi {name},</p>
        <p>Click the button below to confirm your email:</p>
        <p><a href="{url}" style="display:inline-block;padding:10px 20px;background:#007bff;color:#fff;text-decoration:none;border-radius:4px;">Confirm Email</a></p>
        <p>If you didn't register, ignore this message.</p>
    """

    msg = EmailMultiAlternatives(subject, '', settings.DEFAULT_FROM_EMAIL, [target_email])
    msg.attach_alternative(html_content, "text/html")
    msg.send()
