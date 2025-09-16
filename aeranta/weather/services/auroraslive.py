from pprint import pprint

import requests
from django.contrib.contenttypes.models import ContentType
from alerts.models import Checker


def auto_update_auroras():
    from weather.models import AurorasLiveApi
    auroras_ct = ContentType.objects.get_for_model(AurorasLiveApi)
    print('autoupdate auroras')
    user_ids = Checker.objects.filter(
        api=auroras_ct,
        alert__users__isnull=False
    ).values_list('alert__users', flat=True).distinct()
    print(f'AL update for {user_ids}')
    for al in AurorasLiveApi.objects.filter(user_id__in=user_ids):
        al.update_data()


def get_auroras_data(lat, lon):
    a_url = "http://api.auroras.live/v1/"
    params = {
            "type": "all",
            "lat": lat,
            "long": lon,
            "forecast": "false",
            "threeday": "false"
        }

    try:
        response = requests.get(a_url, params=params)
        response.raise_for_status()
        data = response.json()
        ace = data.get('ace')
        current_data = {
            'kp': float(ace.get('kp', 0)),
            'kp1hour': float(ace.get('kp1hour', 0)),
            'kp4hour': float(ace.get('kp4hour', 0)),
            'density': float(ace.get('density', 0)),
            'sw_speed': float(ace.get('speed', 0)),
            'bz': int(ace.get('bz', 0)),
            'probability': data['probability'].get('value', 0),
        }
    except requests.RequestException as e:
        print(f'AurorasLive: {e}')
        current_data = {}
    return current_data


def checkers():
    from weather.models import AurorasLiveApi
    auroras_ct = ContentType.objects.get_for_model(AurorasLiveApi)
    data = get_auroras_data('60.1699', '24.9384')
    for i in data.keys():
        Checker.objects.create(parameter_name=i, api=auroras_ct, description='example')
