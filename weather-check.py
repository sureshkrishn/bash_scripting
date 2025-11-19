import requests
from datetime import datetime

def get_weather(city_name):
    api_key = "3bffb77c5b29c675edf520a418f007a6"  # Replace with your OpenWeatherMap API key
    base_url = "https://api.openweathermap.org/data/2.5/weather"
    complete_url = f"{base_url}?q={city_name}&appid={api_key}&units=metric"
    response = requests.get(complete_url)
    data = response.json()

    # Get current date and time
    now = datetime.now()
    dt_string = now.strftime("%d/%m/%Y %H:%M:%S")

    print(f"Date and Time: {dt_string}")

    if data["cod"] == 200:
        main = data["main"]
        weather_desc = data["weather"][0]["description"]
        temp = main["temp"]
        print(f"Weather in {city_name}:")
        print(f"Temperature: {temp}°C")
        print(f"Description: {weather_desc}")
    else:
        print("City Not Found.")

if __name__ == "__main__":
    city = input("Enter city name: ")
    get_weather(city)
