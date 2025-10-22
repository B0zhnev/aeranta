from datetime import datetime, timedelta


class WindSpeedAlert:
    def __init__(self, user):
        self.user = user
        self.threshold = {'strong': 8, 'gale': 12, 'storm': 17, 'hurricane': 20}

    def check(self):
        winds = []
        try:
            data = self.user.open_weather.forecast_data[0:7]
            local_date = self.user.open_weather.weather_data['local_date']
            local_time = self.user.open_weather.weather_data['local_time']
        except AttributeError:
            return False
        for i in data:
            if i['wind_speed'] >= self.threshold['strong']:
                winds.append({'ld': i['local_date'][:-5],
                              'lt': i['local_time'],
                              'wind_speed': i['wind_speed'],
                              'wind_gust': i['wind_gust']})
        if not winds:
            return False
        maximum = max(winds, key=lambda x: x['wind_speed'])
        starts = f'{winds[0]['lt']}'

        if maximum['wind_speed'] < self.threshold['gale']:
            message = f'Strong Wind! - {maximum['wind_speed']} m/s (with gusts {maximum['wind_gust']} m/s) starts at {starts} with peak at {maximum['lt']}. Be careful!'
        elif maximum['wind_speed'] < self.threshold['storm']:
            message = f'Gale! - {maximum['wind_speed']} m/s (with gusts {maximum['wind_gust']} m/s) starts at {starts} with peak at {maximum['lt']}. Be careful!'
        elif maximum['wind_speed'] < self.threshold['hurricane']:
            message = f'Attention! Storm! - {maximum['wind_speed']} m/s (with gusts {maximum['wind_gust']} m/s) starts at {starts} with peak at {maximum['lt']}. Be careful!'
        else:
            message = f'Attention! Hurricane! - {maximum['wind_speed']} m/s (with gusts {maximum['wind_gust']} m/s) starts at {starts} with peak at {maximum['lt']}. Be careful!'
        return 'Wind Alert', message, local_date, local_time


class BabushkaAlert:
    def __init__(self, user):
        self.threshold = {'med': 9, 'hard': 13}
        self.user = user

    def check(self):
        pressures = []
        try:
            data = self.user.open_weather.forecast_data[0:23:2]
            local_date = self.user.open_weather.weather_data['local_date']
            local_time = self.user.open_weather.weather_data['local_time']
        except AttributeError:
            return False
        for i in data:
            pressures.append({'date': i['local_date'][:-5], 'pressure': int(i['pressure'])})
        maximum = max(pressures, key=lambda x: x['pressure'])
        minimum = min(pressures, key=lambda x: x['pressure'])
        difference = maximum['pressure'] - minimum['pressure']
        message = ''
        first, second = sorted([maximum, minimum], key=lambda x: x['date'])
        if difference < self.threshold['med']:
            return False
        elif difference < self.threshold['hard']:
            message = f'Darling, atmospheric pressure difference is medium - {difference} hPa. From {first['date']} ({first['pressure']} hPa) to {second['date']} ({second['pressure']} hPa)'
        elif difference >= self.threshold['hard']:
            message = f'Darling, atmospheric pressure difference is high! - {difference} hPa. From {first['date']} ({first['pressure']} hPa) to {second['date']} ({second['pressure']} hPa)'
        return 'Babushka Alert', message, local_date, local_time


class IcyRoadAlert:
    def __init__(self, user):
        self.user = user

    def check(self):
        try:
            data = self.user.open_weather.forecast_data[:7]
            local_date = self.user.open_weather.weather_data['local_date']
            local_time = self.user.open_weather.weather_data['local_time']
        except AttributeError:
            return False

        state = None
        events = {}
        for i in data:
            temp = i['temp']
            humidity = i.get('humidity', 50)
            pop = i.get('pop', 0)

            if temp >= 0 and state is None:
                state = False
            elif temp < 0 and state == False:
                state = True
                events.setdefault('refreezing', []).append(i['local_time'])

            if 'rain' in i and (temp - 2) < 0 and pop >= 0.3:
                events.setdefault('freezing_rain', []).append(i['local_time'])

            if -20 < (temp - 2) < 0 and humidity >= 75:
                events.setdefault('black_ice', []).append(i['local_time'])
        
        if not events:
            return False

        if 'freezing_rain' in events and 'black_ice' in events:
            risk = 'Very high risk'
        elif 'freezing_rain' in events or 'black_ice' in events:
            risk = 'High risk'
        else:
            risk = 'Watch out'

        event_names = [k.replace('_', ' ') for k in events.keys()]
        # all_times = [t for times in events.values() for t in times]
        # time = sorted(all_times)[0]
        events_text = ', '.join(event_names).capitalize()
        message = f'{risk}! {events_text} in the next 24 hours. Be careful!'

        return 'Ice Risk Alert', message, local_date, local_time


class DedushkaAlert:
    def __init__(self, user):
        self.user = user

    def check(self):
        try:
            aurora_data = self.user.auroras.current_data
            local_date = self.user.open_weather.weather_data['local_date']
            local_time = self.user.open_weather.weather_data['local_time']
        except AttributeError:
            return False

        kp = aurora_data.get('kp', 0)
        if kp >= 6:
            kp_score = 3
        elif kp >= 4:
            kp_score = 2
        elif kp >= 3:
            kp_score = 1
        else:
            kp_score = 0

        bz = aurora_data.get('bz', 0)
        if bz < -10:
            bz_score = 3
        elif bz < -5:
            bz_score = 2
        elif bz < 0:
            bz_score = 1
        else:
            bz_score = 0

        sw = aurora_data.get('sw_speed', 0)
        if sw >= 600:
            sw_score = 2
        elif sw >= 500:
            sw_score = 1
        else:
            sw_score = 0

        density = aurora_data.get('density', 0)
        if density >= 20:
            density_score = 2
        elif density >= 10:
            density_score = 1
        else:
            density_score = 0

        total_score = kp_score + bz_score + sw_score + density_score
        max_score = 10

        if total_score < 2:
            return False

        if total_score <= 4:
            level_text = "there might be some small effects"
        elif total_score <= 7:
            level_text = "I feel there could be noticeable effects"
        else:
            level_text = "beware! Strong effects might be felt"

        message = (
            f"My dear, {level_text} due to geomagnetic activity. "
            f"My estimate of the risk is {total_score}/{max_score}, take care!"
        )
        return "Dedushka Alert", message, local_date, local_time
        
        
class AuroraAlert:
    def __init__(self, user):
        self.user = user

    def check(self):
        try:
            aurora_data = self.user.auroras.current_data
            weather_data = self.user.open_weather.forecast_data[0]
            sunrise_str = self.user.open_weather.weather_data['sunrise_local']  # hh:mm
            sunset_str = self.user.open_weather.weather_data['sunset_local']    # hh:mm
            local_date_str = self.user.open_weather.weather_data['local_date']  # dd.mm.yyyy
            local_time_str = self.user.open_weather.weather_data['local_time']  # hh:mm
        except AttributeError:
            return False

        try:
            local_date = datetime.strptime(local_date_str, "%d.%m.%Y").date()
            now_dt = datetime.strptime(f"{local_date_str} {local_time_str}", "%d.%m.%Y %H:%M")
            sunrise_dt = datetime.strptime(f"{local_date_str} {sunrise_str}", "%d.%m.%Y %H:%M")
            sunset_dt = datetime.strptime(f"{local_date_str} {sunset_str}", "%d.%m.%Y %H:%M")

            if now_dt < sunrise_dt:
                sunset_dt -= timedelta(days=1)

            if not (now_dt >= sunset_dt or now_dt <= sunrise_dt):
                return False
        except Exception:
            return False

        visibility = weather_data.get('visibility', 10000)
        clouds = weather_data.get('clouds', 0)
        if visibility < 2000 or clouds > 70:
            return False

        kp = aurora_data.get('kp', 0)
        kp1hour = aurora_data.get('kp1hour', 0)
        kp4hour = aurora_data.get('kp4hour', 0)
        bz = aurora_data.get('bz', 0)
        sw_speed = aurora_data.get('sw_speed', 0)
        density = aurora_data.get('density', 0)
        probability = aurora_data.get('probability', 0)

        if probability < 3:
            return False

        # --- Баллы ---
        score = 0
        max_score = 17

        kp_max = max(kp, kp1hour, kp4hour)
        if kp_max >= 6:
            score += 3
        elif kp_max >= 5:
            score += 2
        elif kp_max >= 4:
            score += 1

        if bz <= -5:   # включил -5
            score += 2
        elif -5 < bz < 0:
            score += 1

        if sw_speed > 500:
            score += 2
        elif 400 <= sw_speed <= 500:
            score += 1

        if density > 10:
            score += 2
        elif 5 <= density <= 10:
            score += 1

        # --- Градация уровней ---
        if score < 3:
            return False
        elif 3 <= score <= 6:
            chance_text = "Low chance"
        elif 7 <= score <= 9:
            chance_text = "Decent chance"
        elif 10 <= score <= 12:
            chance_text = "High chance"
        else:
            chance_text = "Very high chance"

        message = (
            f"{chance_text} to see Aurora in the next three hours. "
            f"Our probability estimate is {score} out of {max_score}"
        )

        return "Aurora Alert", message, local_date_str, local_time_str


class LunarAlert:
    def __init__(self, user):
        self.user = user

    def check(self):
        try:
            moon_data = self.user.ipga.current_data
            local_date = self.user.open_weather.weather_data['local_date']
            local_time = self.user.open_weather.weather_data['local_time']
        except AttributeError:
            return False

        try:
            now = datetime.strptime(f'{local_date} {local_time}', "%d.%m.%Y %H:%M").time()
            moonrise = datetime.strptime(f'{local_date} {moon_data.get('moonrise', '00:00')}', "%d.%m.%Y %H:%M").time()
            moonset = datetime.strptime(f'{local_date} {moon_data.get('moonset', '23:59')}', "%d.%m.%Y %H:%M").time()

            if now < moonrise:
                moonset -= timedelta(days=1)

            if not (now >= moonset or now <= moonrise):
                return False

        except Exception:
            return False

        events = []

        phase = moon_data.get('moon_phase', '').lower()
        distance = moon_data.get('moon_distance', 0)
        illumination = moon_data.get('moon_illumination_percentage', 0)

        if phase == 'full_moon':
            events.append('Full')
            if distance and distance < 360000:
                events.append(f'and Super Moon')
            elif distance and distance > 405000:
                events.append(f'and Micro Moon')
            else:
                events.append(f'Moon')

        elif phase == 'new_moon':
            events.append('New Moon')

        elif illumination > 95:
            events.append(f'high illuminated Moon!')

        if not events:
            return False

        if phase == 'new_moon':
            message = f"New Moon phase — invisible from Earth."
        else:
            message = f"Check the {' '.join(events)}! It's visible now!"

        return "Lunar Alert", message, local_date, local_time