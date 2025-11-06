from pprint import pprint
import requests
from django.conf import settings
from alerts.models import Checker
from django.contrib.contenttypes.models import ContentType
from datetime import datetime, timedelta

api_key = settings.OPENWEATHER_API_KEY


def auto_update_openweather():
    from weather.models import OpenWeatherApi
    openweather_ct = ContentType.objects.get_for_model(OpenWeatherApi)
    user_ids = (
        Checker.objects
        .filter(api=openweather_ct)
        .values_list('alert__users', flat=True)
        .distinct()
    )
    print(f'OW update for {user_ids}')
    for ow in OpenWeatherApi.objects.filter(user__id__in=user_ids):
        ow.update_data()


def get_forecast_data(lat, lon):
    url = 'https://api.openweathermap.org/data/2.5/forecast'
    params = {
        'lat': lat,
        'lon': lon,
        'appid': api_key,
        'units': 'metric',
    }
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        forecast = []
        for i in data['list']:
            forecast.append({
                'dt': i.get('dt'),
                'clouds': i['clouds'].get('all'),
                'humidity': i['main'].get('humidity'),
                'pressure': i['main'].get('pressure'),
                'sea_level': i['main'].get('sea_level'),
                'temp': i['main'].get('temp'),
                'temp_kf': i['main'].get('temp_kf'),
                'temp_max': i['main'].get('temp_max'),
                'temp_min': i['main'].get('temp_min'),
                'sys': i['sys'].get('pod'),
                'description': i['weather'][0].get('description'),
                'icon': i['weather'][0].get('icon'),
                'main_description': i['weather'][0].get('main'),
                'wind_speed': i['wind'].get('speed'),
                'wind_deg': i['wind'].get('deg'),
                'wind_gust': i['wind'].get('gust', 0),
                'pop': i.get('pop'),
                'code': i['weather'][0].get('id'),
                'popr': int((i['pop'] * 100)),
                'visibility': i.get('visibility'),
                'local_date': to_local_time(i['dt'], data['city']['timezone'])[0],
                'local_time': to_local_time(i['dt'], data['city']['timezone'])[1],
            })
            if 'rain' in i.keys():
                time, rain = *i['rain'].keys(), *i['rain'].values()
                forecast[-1]['rain'] = str(rain) if rain else 0
                forecast[-1]['rain_time'] = str(time)
    except requests.RequestException as e:
        print(f'OpenWeather: {e}')
        forecast = []

    return forecast


def get_weather_data(lat, lon):
    w_url = 'https://api.openweathermap.org/data/2.5/weather'
    params = {
        'lat': lat,
        'lon': lon,
        'appid': api_key,
        'units': 'metric',
    }
    try:
        response = requests.get(w_url, params=params)
        response.raise_for_status()
        weather_data = response.json()
        weather = {
            'dt': weather_data.get('dt'),
            'coord': weather_data.get('coord'),
            'city': weather_data.get('name'),
            'sunrise': weather_data['sys'].get('sunrise'),
            'sunset': weather_data['sys'].get('sunset'),
            'timezone': weather_data.get('timezone'),
            'visibility': weather_data.get('visibility'),
            'cod': weather_data.get('cod'),
            'clouds': weather_data['clouds'].get('all'),
            'feels_like': weather_data['main'].get('feels_like'),
            'grnd_level': weather_data['main'].get('grnd_level'),
            'humidity': weather_data['main'].get('humidity'),
            'pressure': weather_data['main'].get('pressure'),
            'sea_level': weather_data['main'].get('sea_level'),
            'temp': weather_data['main'].get('temp'),
            'temp_max': weather_data['main'].get('temp_max'),
            'temp_min': weather_data['main'].get('temp_min'),
            'description': weather_data['weather'][0].get('description'),
            'icon': weather_data['weather'][0].get('icon'),
            'main_description': weather_data['weather'][0].get('main'),
            'wind': weather_data['wind'].get('speed'),
            'wind_deg': weather_data['wind'].get('deg'),
            'gust': weather_data['wind'].get('gust', 0),
            'country': weather_data['sys'].get('country', 'N/A')
        }

        if 'rain' in weather_data.keys():
            time, rain = *weather_data['rain'].keys(), *weather_data['rain'].values()
            weather['rain'] = str(rain)
            weather['rain_time'] = str(time).strip('h')

        if 'snow' in weather_data.keys():
            time, snow = *weather_data['snow'].keys(), *weather_data['snow'].values()
            weather['snow'] = str(snow)
            weather['snow'] = str(time).strip('h')
    except requests.RequestException as e:
        print(f'OpenWeather: {e}')
        weather = {}
    weather['sunrise_local'] = to_local_time(weather['sunrise'], weather['timezone'])[1]
    weather['sunset_local'] = to_local_time(weather['sunset'], weather['timezone'])[1]
    weather['local_date'], weather['local_time'] = to_local_time(weather['dt'], weather['timezone'])

    return weather


def to_local_time(dt, timezone):
    local_dt = datetime.fromtimestamp(dt - 7200) + timedelta(seconds=timezone)
    localdate = local_dt.strftime('%d.%m.%Y')
    localtime = local_dt.strftime('%H:%M')
    return localdate, localtime
