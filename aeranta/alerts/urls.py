from django.urls import path
from django.views.decorators.cache import cache_page
from django.views.decorators.cache import never_cache
from .views import AlertListView, ToggleAlertSubscriptionView

app_name = 'alerts'

urlpatterns =[
    path('', never_cache(AlertListView.as_view()), name='list'),
    path('toggle/<slug:slug>/', ToggleAlertSubscriptionView.as_view(), name='toggle')
]
