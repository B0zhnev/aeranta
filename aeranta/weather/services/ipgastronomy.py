from pprint import pprint
from django.contrib.contenttypes.models import ContentType
from django.conf import settings
import requests
from alerts.models import Checker


api_key = settings.IPGASTRONOMY_API_KEY


def get_astronomy_data(lat, lon):
    api_url = "https://api.ipgeolocation.io/astronomy"
    params = {
        "apiKey": api_key,
        "lat": lat,
        "long": lon
    }
    try:
        response = requests.get(api_url, params=params)
        response.raise_for_status()
        data = response.json()
        current_data = {
            'day_length': data.get('day_length'),
            'elevation': data.get('location', {}).get('elevation', 0),
            'moon_altitude':  round(data.get('moon_altitude'), 2),
            'moon_angle':  round(data.get('moon_angle'), 2),
            'moon_azimuth': round(data.get('moon_azimuth'), 2),
            'moon_distance': round(data.get('moon_distance'), 2),
            'moon_illumination_percentage': abs(float(data.get('moon_illumination_percentage', 0))),
            'moon_parallactic_angle': round(data.get('moon_parallactic_angle'), 2),
            'moon_phase': data.get('moon_phase'),
            'moon_status': data.get('moon_status'),
            'moonrise': data.get('moonrise'),
            'moonset': data.get('moonset'),
            'solar_noon': data.get('solar_noon'),
            'sun_altitude': round(data.get('sun_altitude'), 2),
            'sun_azimuth': data.get('sun_azimuth'),
            'sun_distance': data.get('sun_distance'),
            'sun_status': data.get('sun_status'),
            'front_phase': str(data.get('moon_phase')).replace('_', ' ').lower().capitalize()
        }
    except requests.RequestException as e:
        print(f'IPGAstronomy: {e}')
        current_data = {}
    return current_data


def auto_update_ipgastronomy():
    from weather.models import IPGAstronomyApi
    ipgastronomy_ct = ContentType.objects.get_for_model(IPGAstronomyApi)
    print('autoupdate ipgastronomy')
    user_ids = Checker.objects.filter(
        api=ipgastronomy_ct,
        alert__users__isnull=False
    ).values_list('alert__users', flat=True).distinct()
    print(f'IPGA update for {user_ids}')
    for ipga in IPGAstronomyApi.objects.filter(user_id__in=user_ids):
        ipga.update_data()


def checkers():
    from weather.models import IPGAstronomyApi
    ipgastronomy_ct = ContentType.objects.get_for_model(IPGAstronomyApi)
    data = get_astronomy_data('60.1699', '24.9384')
    for i in data.keys():
        Checker.objects.create(parameter_name=i, api=ipgastronomy_ct, description='example')