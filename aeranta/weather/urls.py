from django.urls import path
from . import views
from django.views.decorators.cache import cache_page
urlpatterns = [
    path('', views.index, name='home'),
    path('weather-at-point/', views.weather_at_point, name='weather_at_point'),
    path('contacts/', views.show_contacts, name='contacts'),
    # path('demo/', views.demo, name='demo'),
]
