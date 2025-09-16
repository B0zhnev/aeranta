from django.contrib.auth.views import LogoutView, PasswordResetDoneView, PasswordResetCompleteView
from django.urls import path
from . import views, views_email
from .views_email import ConfirmedEmailPasswordResetView, PasswordResetCf, post_registration
from django.views.decorators.cache import never_cache
app_name = "users"

urlpatterns = [
    path('login/', views.LoginUser.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('register/', views.RegisterUser.as_view(), name='register'),
    path('user/', never_cache(views.ProfileUser.as_view()), name='profile'),
    path('update-location/', views.update_location, name='update_location'),
    path('user/forecast/', views.ProfileForecastBlock.as_view(), name='forecast_block'),
    path('user/edit-profile/', never_cache(views.EditProfileView.as_view()), name='edit_profile'),
    path('post_registration/', post_registration, name='post_registration'),
    path('confirm_email_prompt/', views_email.confirm_email_prompt, name='confirm_email_prompt'),
    path('confirm_email_skip/', views_email.confirm_email_skip, name='confirm_email_skip'),
    path('confirm_email_instructions_sent/', views_email.confirm_email_instructions_sent,
         name='confirm_email_instructions_sent'),
    path('confirm_email/<str:token>/', views_email.confirm_email_token_view, name='confirm_email'),
    path('confirm_email_token/<str:token>/', views_email.confirm_email_token_view, name='confirm_email_token'),
    # Password reset URLs
    path('password-reset/', ConfirmedEmailPasswordResetView.as_view(), name='password_reset'),
    path('password-reset/done/',
         PasswordResetDoneView.as_view(template_name='users/password_reset_done.html'),
         name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/',
         PasswordResetCf.as_view(),
         name='password_reset_confirm'),
    path('password-reset-complete/',
         PasswordResetCompleteView.as_view(template_name='users/password_reset_complete.html'),
         name='password_reset_complete'),
]
