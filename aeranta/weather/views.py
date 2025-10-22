from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.cache import never_cache
from notifications.services import send_scheduled_notifications
from .services import openweather
from django.views.decorators.cache import never_cache

@never_cache
def index(request):
    return render(request, 'weather/index.html')


def weather_at_point(request):
    try:
        lat = float(request.GET['lat'])
        lon = float(request.GET['lon'])

    except (KeyError, ValueError):
        return JsonResponse({'error': 'Wrong coordinates'}, status=400)
    current = openweather.get_weather_data(lat, lon)
    forecast = openweather.get_forecast_data(lat, lon)
    data = {'current': current, 'forecast': forecast}
    return JsonResponse(data)


@never_cache
def show_contacts(request):
    return render(request, 'weather/visit.html')


@never_cache
def demo(request):
    return render(request, 'weather/demo.html')