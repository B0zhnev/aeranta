from pprint import pprint
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.db import models
from .services import openweather, auroraslive, ipgastronomy


class OpenWeatherApi(models.Model):
    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE, related_name='open_weather')
    weather_data = models.JSONField(default=dict)
    forecast_data = models.JSONField(default=dict)
    last_updated = models.DateTimeField(default=timezone.now)
    timezone = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return f'OpenWeather for {self.user.username}'

    def update_data(self):
        lat = self.user.location.y
        lon = self.user.location.x
        self.weather_data = openweather.get_weather_data(lat, lon)
        self.forecast_data = openweather.get_forecast_data(lat, lon)
        self.last_updated = timezone.now()
        self.timezone = self.weather_data['timezone']
        self.save()
        print(f'OpenWeatherApi: data was updated for {self.user.username}')


class AurorasLiveApi(models.Model):
    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE, related_name='auroras')
    current_data = models.JSONField(default=dict)
    last_updated = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f'AurorasLive for {self.user.username}'

    def update_data(self):
        lat = self.user.location.y
        lon = self.user.location.x
        self.current_data = auroraslive.get_auroras_data(lat, lon)
        self.last_updated = timezone.now()
        self.save()
        print(f'AurorasLiveApi: data was updated for {self.user.username}')
        
        
class IPGAstronomyApi(models.Model):
    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE, related_name='ipga')
    current_data = models.JSONField(default=dict)
    last_updated = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f'IPGAstronomyApi for {self.user.username}'

    def update_data(self):
        lat = self.user.location.y
        lon = self.user.location.x
        self.current_data = ipgastronomy.get_astronomy_data(lat, lon)
        self.last_updated = timezone.now()
        self.save()
        print(f'IPGAstronomyApi: data was updated for {self.user.username}')
