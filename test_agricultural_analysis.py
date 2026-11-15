import requests

OVERPASS_URL = "https://overpass-api.de/api/interpreter"
AGRICULTURE_SEARCH_RADIUS_METERS = 25_000

def get_agr_feature(latitude, longitude):

    query = f"""
    [out:json][timeout:10];
    (
      nwr(around:{AGRICULTURE_SEARCH_RADIUS_METERS},{latitude},{longitude})
        ["landuse"~"^(farmland|orchard|vineyard|meadow|plant_nursery|greenhouse_horticulture|paddy)$"];
      nwr(around:{AGRICULTURE_SEARCH_RADIUS_METERS},{latitude},{longitude})
        ["crop"];
    );
    out tags center;
    """

    overpass_servers = [
        "https://overpass.kumi.systems/api/interpreter",
        "https://overpass-api.de/api/interpreter"
    ]

    headers = {
        "User-Agent": "WeatherForecastingSystem/1.0",
        "Accept": "application/json"
    }

    for server in overpass_servers:

        try:
            response = requests.post(server,data={"data": query},headers=headers,timeout=12)
            print("Server:", server)
            print("Status:", response.status_code)
            print("Response:", response.text[:500])

            response.raise_for_status()

            data = response.json()

            return data.get("elements", [])

        except (requests.RequestException, ValueError) as e:
            print(f"Overpass request failed ({server}): {e}")

    return None

def check_agr_relevance(latitude,longitude):
    try:
        latitude = float(latitude)
        longitude = float(longitude)

        if not(-90<=latitude<=90):
            return None
        if not (-180<=longitude<=180):
            return None

        elements= get_agr_feature(latitude, longitude)
        print("Number of agricultural features:", len(elements))
        if elements is None:
            return None

        feature_types=set()
        for ele in elements:
            tags=ele.get("tags",{})
            landuse=tags.get("landuse")
            crop=tags.get("crop")
            if landuse:
                feature_types.add(landuse)
            elif crop:
                feature_types.add("crop tagged land")

        result =None
        if elements:
            result={
                "is_relevant":True,
                "feature_count":len(elements),
                "feature_type":sorted(feature_types),
                "search_radius_km": AGRICULTURE_SEARCH_RADIUS_METERS/1000
            }
        return result
    except (TypeError,ValueError):
        return None

def calculate_suitability(weather_data):

    if not isinstance(weather_data, dict):
        return None

    temperature = weather_data.get("temperature_2m")

    if temperature is None:
        return None

    #either Kelvin or Celsius
    temp_c = float(temperature)

    if temp_c > 100:
        temp_c -= 273.15

    humidity = weather_data.get("relative_humidity_2m")
    wind_speed = weather_data.get("wind_speed_10m")

    if 15 <= temp_c <= 30:
        temp_score = 100
    elif 10 <= temp_c <= 35:
        temp_score = 70
    else:
        temp_score = 40

    available_scores = [temp_score]

    if humidity is not None:
        humidity = float(humidity)
        if 40 <= humidity <= 80:
            humidity_score = 100
        elif 25 <= humidity <= 90:
            humidity_score = 70
        else:
            humidity_score = 40
        available_scores.append(humidity_score)
    if wind_speed is not None:
        if wind_speed <= 5:
            wind_score = 100
        elif wind_speed <= 10:
            wind_score = 70
        else:
            wind_score = 40
        available_scores.append(wind_score)

    return {
        "score": round(sum(available_scores) / len(available_scores)),
        "temperature": round(temp_c, 1),
        "humidity": humidity,
        "wind_speed": wind_speed,
        "wind_direction": weather_data.get("wind_direction_10m"),
        "pressure": weather_data.get("pressure_msl")
    }


def analyse_weather_risks(weather_data, forecast_data=None):
    #identifying forecast based weather indicators

    risks = []
    max_rain_probability = None
    max_temperature = None
    min_temperature = None
    max_wind_speed = None

    if isinstance(forecast_data, dict):
        rain_probabilities = forecast_data.get("precipitation_probability_max", [])
        max_temperatures = forecast_data.get("temperature_2m_max", [])
        min_temperatures = forecast_data.get("temperature_2m_min", [])
        wind_speeds = forecast_data.get("wind_speed_10m_max", [])

        if isinstance(rain_probabilities, list) and rain_probabilities:
            valid_values = [float(value) for value in rain_probabilities if value is not None]
            if valid_values:
                max_rain_probability = max(valid_values)

        if isinstance(max_temperatures, list) and max_temperatures:
            valid_values = [float(value) for value in max_temperatures if value is not None]
            if valid_values:
                max_temperature = max(valid_values)

        if isinstance(min_temperatures, list) and min_temperatures:
            valid_values = [float(value) for value in min_temperatures if value is not None]
            if valid_values:
                min_temperature = min(valid_values)

        if isinstance(wind_speeds, list) and wind_speeds:
            valid_values = [float(value) for value in wind_speeds if value is not None]
            if valid_values:
                max_wind_speed = max(valid_values)

    if max_rain_probability is not None and max_rain_probability >= 70:
        risks.append(
            "High probability of precipitation is forecast. "
            "Monitor local weather updates and field drainage."
        )

    if max_temperature is not None and max_temperature >= 35:
        risks.append(
            "High-temperature conditions may increase crop heat stress "
            "and water requirements."
        )

    if min_temperature is not None and min_temperature <= 5:
        risks.append(
            "Low temperatures are forecast. Check crop-specific cold "
            "and frost sensitivity."
        )

    if max_wind_speed is not None and max_wind_speed >= 36:
        risks.append(
            "Strong winds are forecast. Take care with spraying and "
            "exposed field operations."
        )

    if not risks:
        risks.append(
            "No major risks were identified by the available weather "
            "indicators. This does not guarantee low risk."
        )

    return {
        "risks": risks,
        "max_rain_probability": (round(max_rain_probability)if max_rain_probability is not None else None),
        "max_temperature": max_temperature,
        "min_temperature": min_temperature,
        "max_wind_speed": max_wind_speed
    }


def generate_recommendations(suitability, risks):

    recommendations = []

    if suitability["temperature"] >= 35:
        recommendations.append(
            "Review crop-specific heat-stress guidance and irrigation requirements."
        )

    humidity = suitability["humidity"]

    if humidity is not None and humidity >= 85:
        recommendations.append(
            "Monitor crops for conditions favourable to humidity-related plant diseases."
        )

    wind_speed = suitability["wind_speed"]
    if wind_speed is not None and wind_speed >= 36:
        recommendations.append(
            "Check wind conditions before spraying or carrying out exposed field operations."
        )

    if risks["max_rain_probability"] is not None and risks["max_rain_probability"] >= 70:
        recommendations.append(
            "Check field drainage and local rainfall warnings."
        )

    if not recommendations:
        recommendations.append(
            "Compare the current weather conditions with the requirements of the crops being cultivated."
        )

    return recommendations

def analyse_agriculture(latitude,longitude,weather_data,forecast_data=None):
    #main analysing function
    try:
        latitude=float(latitude)
        longitude=float(longitude)

        if not (-90<=latitude<=90):
            return None
        if not (-180<=longitude<=180):
            return None

        print("Starting agricultural analysis...")

        relevance = check_agr_relevance(latitude, longitude)
        print("Relevance result:", relevance)

        if not relevance or not relevance.get("is_relevant", False):
            print("Agricultural analysis skipped.")
            return None

        suitability = calculate_suitability(weather_data)
        print("Suitability result:", suitability)

        if suitability is None:
            print("Suitability calculation failed.")
            return None

        risks = analyse_weather_risks(weather_data, forecast_data)
        print("Risk analysis:", risks)

        recommendations = generate_recommendations(suitability, risks)
        print("Recommendations:", recommendations)

    except (TypeError, ValueError, KeyError, IndexError):
        return None

