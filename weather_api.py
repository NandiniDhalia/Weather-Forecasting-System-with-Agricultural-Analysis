import requests

GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
WEATHER_URL = "https://api.open-meteo.com/v1/forecast"
REQUEST_TIMEOUT = 10

def get_location(city):
    if not isinstance(city, str) or not city.strip():
        raise ValueError("Enter a valid city name.")
    clean_city = city.strip()
    params = {
        "name": clean_city,
        "count": 1,
        "language": "en",
        "format": "json"
    }
    response=requests.get(GEOCODING_URL,params=params, timeout=REQUEST_TIMEOUT)
    response.raise_for_status()

    try:
        data=response.json()
    except ValueError as e:
        raise ValueError("Recieved an invalid response from the location service.") from e
    results=data.get("results")
    if not results:
        raise ValueError("City not found. Please enter the correct city name.")
    location = next((item for item in results if item.get("name","").casefold() == clean_city.casefold()), results[0])

    return {
        "name": location["name"],
        "admin1": location.get("admin1", ""),
        "country": location.get("country", ""),
        "latitude": location["latitude"],
        "longitude": location["longitude"],
        "timezone": location.get("timezone", "auto")
    }

def get_weather(city):

    location = get_location(city)

    latitude= location["latitude"]
    longitude= location["longitude"]

    params = {
        "latitude": latitude,
        "longitude": longitude,
        "current": (
            "temperature_2m,relative_humidity_2m,apparent_temperature,"
            "precipitation,weather_code,wind_speed_10m,wind_direction_10m,pressure_msl"
        ),
        "hourly": "relative_humidity_2m,temperature_2m,precipitation_probability",
        "daily": (
            "temperature_2m_max,temperature_2m_min,precipitation_sum,"
            "precipitation_probability_max,weather_code,wind_speed_10m_max"
        ),
        "forecast_days": 7,
        "timezone": "auto"
    }

    response = requests.get(WEATHER_URL, params=params, timeout=REQUEST_TIMEOUT)
    response.raise_for_status()

    try:
        data = response.json()
    except ValueError as exc:
        raise ValueError("Received an invalid response from the weather service.") from exc

    if "current" not in data or "daily" not in data or "hourly" not in data:
        raise ValueError("Weather data is incomplete.")

    return {
        "location": location,
        "latitude": latitude,
        "longitude": longitude,
        "current": data["current"],
        "hourly": data["hourly"],
        "daily": data["daily"],
        "coordinates": (longitude, latitude)
    }


