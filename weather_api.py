import requests

GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
WEATHER_URL = "https://api.open-meteo.com/v1/forecast"
REQUEST_TIMEOUT = 10

INDIAN_STATE_CAPITALS = {
    "goa": ("Panaji", "Goa"),
    "kerala": ("Thiruvananthapuram", "Kerala"),
    "punjab": ("Chandigarh", "Punjab"),
    "haryana": ("Chandigarh", "Haryana"),
    "rajasthan": ("Jaipur", "Rajasthan"),
    "gujarat": ("Gandhinagar", "Gujarat"),
    "maharashtra": ("Mumbai", "Maharashtra"),
    "tamil nadu": ("Chennai", "Tamil Nadu"),
    "karnataka": ("Bengaluru", "Karnataka"),
    "uttar pradesh": ("Lucknow", "Uttar Pradesh"),
    "bihar": ("Patna", "Bihar"),
    "west bengal": ("Kolkata", "West Bengal"),
    "assam": ("Guwahati", "Assam"),
    "madhya pradesh": ("Bhopal", "Madhya Pradesh"),
    "telangana": ("Hyderabad", "Telangana"),
}


def get_location(city):
    if not isinstance(city, str) or not city.strip():
        raise ValueError("Please enter a valid city name.")

    clean_city = city.strip()
    state_entry = INDIAN_STATE_CAPITALS.get(clean_city.casefold())
    search_query = state_entry[0] if state_entry else clean_city

    params = {
        "name": search_query,
        "count": 10,
        "language": "en",
        "format": "json"
    }

    response = requests.get(GEOCODING_URL, params=params, timeout=REQUEST_TIMEOUT)
    response.raise_for_status()

    try:
        data = response.json()
    except ValueError as exc:
        raise ValueError("Received an invalid response from the location service.") from exc

    results = data.get("results", [])
    if not results:
        raise ValueError("City not found. Please enter a valid city name.")

    if state_entry:
        capital_name, state_name = state_entry
        location = next(
            (
                item for item in results
                if item.get("country") == "India"
                and item.get("name", "").casefold() == capital_name.casefold()
            ),
            results[0]
        )
        return {
            "name": clean_city.title(),
            "admin1": state_name,
            "country": "India",
            "latitude": location["latitude"],
            "longitude": location["longitude"],
            "timezone": location.get("timezone", "auto")
        }

    # Prefer exact case-insensitive match in India first, then any exact match
    exact_india = next(
        (
            item for item in results
            if item.get("name", "").casefold() == clean_city.casefold()
            and item.get("country") == "India"
        ),
        None
    )
    exact_global = next(
        (item for item in results if item.get("name", "").casefold() == clean_city.casefold()),
        None
    )
    location = exact_india or exact_global or results[0]

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

    latitude = location["latitude"]
    longitude = location["longitude"]

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