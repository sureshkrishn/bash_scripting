import requests
from datetime import datetime

def get_weather(city_name, weather_api_key):
    base_url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        'q': city_name,
        'appid': weather_api_key,
        'units': 'metric'
    }
    response = requests.get(base_url, params=params)
    if response.status_code == 200:
        data = response.json()
        weather = data['weather'][0]['description']
        temp = data['main']['temp']
        return f"{weather.capitalize()}, {temp}°C"
    else:
        return "Weather data not found."

def get_time_and_date(city_name):
    time_url = f"http://worldtimeapi.org/api/timezone"
    # This part fetches available timezones
    tz_response = requests.get(time_url)
    if tz_response.status_code == 200:
        timezones = tz_response.json()
        matched = [tz for tz in timezones if city_name.replace(" ", "_").capitalize() in tz]
        if matched:
            t_response = requests.get(f"{time_url}/{matched[0]}")
            if t_response.status_code == 200:
                time_data = t_response.json()
                date_time = time_data['datetime']
                dt = datetime.fromisoformat(date_time[:-1])
                return f"{dt.strftime('%Y-%m-%d %H:%M:%S')}"
    return "Time and date not found."

def main():
    weather_api_key = "eceaa3f9d3158fce42b94e62a6393cdc"
    city = input("Enter the city name: ")
    weather = get_weather(city, weather_api_key)
    datetime_str = get_time_and_date(city)
    print(f"\nWeather in {city}: {weather}")
    print(f"Local date and time in {city}: {datetime_str}")

if __name__ == "__main__":
    main()
