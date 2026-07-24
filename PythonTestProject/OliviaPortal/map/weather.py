import requests

import requests


def find_weather(city_name):
    try:
        # 1. First API call: Convert city name to latitude & longitude
        geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city_name}&count=1&language=en&format=json"
        geo_response = requests.get(geo_url)
        geo_data = geo_response.json()

        # Check if city was found
        if not geo_data.get("results"):
            return f"Could not find coordinates for {city_name}", 20.0, 0.0

        location = geo_data["results"][0]
        lat = location["latitude"]
        lng = location["longitude"]

        # 2. Second API call: Get weather for those coordinates
        weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lng}&current=temperature_2m,relative_humidity_2m,weather_code"
        weather_response = requests.get(weather_url)
        weather_data = weather_response.json()

        current = weather_data.get("current", {})
        temp = current.get("temperature_2m", "N/A")

        weather_info = f"Weather in {city_name}: {temp}°C"

        # ALWAYS return exactly 3 values in a tuple:
        return weather_info, lat, lng

    except Exception as e:
        print(f"Error fetching weather: {e}")
        # Fallback values if anything breaks
        return f"Error loading weather for {city_name}", 20.0, 0.0

def get_countries():
    # 1. Define the REST Countries endpoint
    url = "https://raw.githubusercontent.com/dr5hn/countries-states-cities-database/master/json/countries.json"

    try:
        # 2. Send the GET request

        response = requests.get(url)
        if response.status_code == 200:
            countries = response.json()
            print(f"Total countries: {len(countries)}")
            return countries

    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return f"An error occurred"
