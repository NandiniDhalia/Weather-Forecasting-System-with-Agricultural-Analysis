import requests

GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
WEATHER_URL = "https://api.open-meteo.com/v1/forecast"

def get_location(city):
    """Find the coordinates of a city."""
    params = {
        "name": city,
        "count": 1,
        "language": "en",
        "format": "json"
    }

    response = requests.get(
        GEOCODING_URL,
        params=params,
        timeout=15
    )
    response.raise_for_status()

    results = response.json().get("results", [])

    if not results:
        raise ValueError("City not found. Please enter a valid city name.")

    location = results[0]

    return {
        "name": location["name"],
        "country": location.get("country", ""),
        "latitude": location["latitude"],
        "longitude": location["longitude"],
        "timezone": location.get("timezone", "auto")
    }

def get_weather(city):
    """Retrieve current weather and a seven-day forecast."""

    location = get_location(city)

    params = {
        "latitude": location["latitude"],
        "longitude": location["longitude"],
        "current": (
            "temperature_2m,"
            "relative_humidity_2m,"
            "apparent_temperature,"
            "weather_code,"
            "pressure_msl,"
            "wind_speed_10m,"
            "wind_direction_10m"
        ),
        "hourly":"relative_humidity_2m",
        "daily": (
            "weather_code,"
            "temperature_2m_max,"
            "temperature_2m_min,"
            "precipitation_probability_max,"
            "wind_speed_10m_max"
        ),
        "forecast_days": 7,
        "timezone": "auto"
    }

    response = requests.get(
        WEATHER_URL,
        params=params,
        timeout=15
    )
    response.raise_for_status()

    data = response.json()

    if "current" not in data or "daily" not in data:
        raise ValueError("Weather data is incomplete.")

    return {
        "location": location,
        "latitude": location["latitude"],
        "longitude": location["longitude"],
        "current": data["current"],
        "hourly": data["hourly"],
        "daily": data["daily"],
        "coordinates": (location["longitude"], location["latitude"])
    }


