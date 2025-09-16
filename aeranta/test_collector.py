from alerts.alerts import WindSpeedAlert, BabushkaAlert, IcyRoadAlert, AuroraAlert, DedushkaAlert

ALERT_CLASSES = {
    'wind_alert': WindSpeedAlert,
    'babushka': BabushkaAlert,
    'icy_road': IcyRoadAlert,
    'aurora': AuroraAlert,
    'dedushka': DedushkaAlert
}


def run_alert_for_user(user, alert_class):
    alert_instance = alert_class(user)
    return alert_instance.check()


def collector(users):
    for user in users:
        for slug, alert_class in ALERT_CLASSES.items():
            result = run_alert_for_user(user, alert_class)
            if result:
                sender, message, local_date, local_time = result
                print(f"[{slug}] ALERT TRIGGERED:\nMessage: {message}\nDate: {local_date} Time: {local_time}\n")
            else:
                print(f"[{slug}] No alert for {user}\n")


if __name__ == "__main__":
    from types import SimpleNamespace

    user = SimpleNamespace(
        open_weather=SimpleNamespace(
            forecast_data=[
                {'wind_speed': 10, 'wind_gust': 13.6, 'local_date': '25.08.2025', 'local_time': '21:00', 'pressure': 990,
                 'temp': -2, 'humidity': 80, 'pop': 0.5, 'rain': True, 'visibility': 10000, 'clouds': 20},

                {'wind_speed': 15, 'wind_gust': 19, 'local_date': '26.08.2025', 'local_time': '0:00', 'pressure': 1000,
                 'temp': 1, 'humidity': 60, 'pop': 0, 'rain': False, 'visibility': 8000, 'clouds': 10},

                {'wind_speed': 30, 'wind_gust': 35.1, 'local_date': '26.08.2025', 'local_time': '3:00',
                 'pressure': 990, 'temp': -2, 'humidity': 80, 'pop': 0.5, 'rain': True, 'visibility': 10000,
                 'clouds': 20},

                {'wind_speed': 15, 'wind_gust': 19, 'local_date': '26.08.2025', 'local_time': '6:00', 'pressure': 1000,
                 'temp': 1, 'humidity': 60, 'pop': 0, 'rain': False, 'visibility': 8000, 'clouds': 10},

                {'wind_speed': 19, 'wind_gust': 25.3, 'local_date': '26.08.2025', 'local_time': '8:00', 'pressure': 1030,
                 'temp': -1, 'humidity': 80, 'pop': 0.5, 'rain': True, 'visibility': 10000, 'clouds': 20},
            ],
            weather_data={
                'sunrise': 1756090074,
                'sunset': 1756177306,
                'local_date': '25.08.2025',
                'local_time': '19:00'
            }
        ),
        auroras=SimpleNamespace(
            current_data={'kp': 3, 'kp1hour': 5, 'kp4hour': 4, 'bz': -5, 'sw_speed': 400, 'density': 5, 'probability': 100}
        )
    )

    collector([user])
