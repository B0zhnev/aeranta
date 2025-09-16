from django.urls import path
from . import views
from django.views.decorators.cache import never_cache


app_name = 'notifications'

urlpatterns = [
     path('', never_cache(views.NotificationListView.as_view()), name='list'),
     path('mark-read/<int:pk>/', views.MarkReadView.as_view(), name='mark_read'),
     path('mark-all-read/', views.AllMarkReadView.as_view(), name='mark_all_read'),
     path('email-notifications/', views.edit_email_notifications, name='edit_email_notifications'),
]
