from datetime import datetime
import requests

from environs import Env

from country import COUNTRY_CODES

env = Env()
env.read_env()

API_TOKEN = env.str("WEATHER_TOKEN")


def get_weather_date(city_name: str) -> str:
    # OpenWeather API xizmatiga so'rov yuborish
    rain_comment = ""
    response = requests.get(url=f"https://api.openweathermap.org/data/2.5/weather?q={city_name}&appid={API_TOKEN}&units=metric")

    # Status kodni tekshirish
    if response.status_code == 200:
        weather_data = response.json()  # { ... }
        country_code = weather_data.get('sys').get('country')
        flag, country_name = COUNTRY_CODES.get(country_code, (", "))

        sunrise_seconds = weather_data.get("sys").get("sunrise")
        sunset_seconds = weather_data.get("sys").get("sunset")
        
        wind_data = weather_data.get('wind', {})
        wind_speed = wind_data.get('speed', 0)

        sunrise = datetime.fromtimestamp(timestamp=sunrise_seconds).strftime("%H:%M:%S")
        sunset = datetime.fromtimestamp(timestamp=sunset_seconds).strftime("%H:%M:%S")
        
        
        altitude = weather_data.get('main', {}).get('sea_level') 
        if altitude:
            altitude_text = f"{altitude} metr\n"
        else:
            altitude_text = "Malumot yo'q" 
            
        
        rain_data = weather_data.get('rain', {})
        rain_1h = rain_data.get('1h', 0)  

        if rain_1h > 0:
            if rain_1h < 2.5:
                rain_comment = "🌦️ Juda sekin yomg'ir yogʻyapti"
            elif rain_1h < 10:
                rain_comment = "🌧️ Oʻrtacha yomgʻir yogʻyapti. Soyabon olib oling!"
            else:
                rain_comment = "⛈️ Juda kuchli jala quymoqda! Ehtiyot boʻling."
                
            rain_line = f"🌧️ Yomgʻir (1 soatda): {rain_1h} mm ({rain_comment})\n"
        else:
            rain_line = "☀️ Hozircha yogʻingarchilik kutilmayapti"

        result = f"""
🌆 Bugun {flag if flag else ' '} {country_name},  {city_name} da

🌤️ Harorat: {weather_data.get('main').get('temp')} C
🌤️ Minimal harorat: {weather_data.get('main').get('temp_min')} C
🌤️ Maksimal harorat: {weather_data.get('main').get('temp_max')} C

䷮ Bosim: {weather_data.get('main').get('pressure')} Pa
💧 Namlik: {weather_data.get('main').get('humidity')} %
💨 Shamol tezligi: {wind_speed} m/s
⛰️ Dengiz sathidan balandligi: {altitude_text}
{rain_line}

🌅 Quyoshning chiqish vaqti: {sunrise} da
🌄 Quyoshning botish vaqti: {sunset} da
"""
        return result, True

    else:
        return f"\"{city_name}\" nomli shahar topilmadi", False
    
