import os
import requests

BASE_URL = "https://api.agromonitoring.com/agro/1.0"
API_KEY = os.getenv("AGROMONITORING_API_KEY")
def api_get(endpoint, params=None):
    #Fetch data from the aagromonitoring api
    if not API_KEY:
        return None

    query = dict(params or {})
    query["appid"] = API_KEY

    try:
        response = requests.get(f"{BASE_URL}/{endpoint}", params=query, timeout=15)
        response.raise_for_status()
        return response.json()
    except (requests.RequestException, ValueError):
        return None

def point_in_polygon(longitude, latitude, coordinates):
    #check whether a point falls inside a polygon ring
    inside=False
    j=len(coordinates)-1
    for i in range(len(coordinates)):
        lon_i, lat_i = coordinates[i]
        lon_j, lat_j = coordinates[j]

        intersects = ((lat_i > latitude) != (lat_j > latitude)) and longitude < (lon_j - lon_i) * (latitude - lat_i) / ((lat_j - lat_i) or 1e-12) + lon_i

        if intersects:
            inside = not inside
        j=i
    return inside

def polygon_cont_loc(polygon, latitude, longitude):
    #check a location against a registered polygon
    geo_json = polygon.get("geo_json",{})
    geometry = geo_json.get("geometry", geo_json)

    if geometry.get("type") != "Polygon":
        return False

    rings = geometry.get("coordinates",[])

    if not rings:
        return False

    inside_outer = point_in_polygon(longitude, latitude, rings[0])

    if not inside_outer:
        return False

    for hole in rings[1:]:
        if point_in_polygon(longitude, latitude, hole):
            return False

    return True

def check_agri_relevance(latitude, longitude):
    #returns none if no polygon contains loc. otherwise matching polygon returned
    polygons = api_get("polygons")
    if not isinstance(polygons, list):
        return None
    for polygon in polygons:
        if polygon_cont_loc(polygon, latitude, longitude):
            return polygon
    return None


def calculate_suitability(weather_data):
    current = weather_data["current"]
    main = weather_data["main"]
    wind = current.get("wind",{})

    temp = main.get("temp")
    if temp is None:
        return None
    temp_c = temp - 273.15
    humidity = main.get("humidity")
    wind_speed = wind.get("speed",0)

    temp_score = ( 100 if 15<= temp_c <= 30 else 70 if 10<= temp_c <= 35 else 40)
    humidity_score= (100 if humidity is not None and 40 <= humidity <=80 else 65 if humidity is not None and 25<= humidity <=90 else 40)
    wind_score = (100 if wind_speed<=5 else 70 if wind_speed <=10 else 40)

    score = round((temp_score + humidity_score+wind_score)/3)

    return {
        "score":score,
        "temperature":round(temp_c,1),
        "humidity":humidity,
        "wind_speed":wind_speed,
        "wind_direction":wind.get("deg"),
        "pressure":main.get("pressure")
    }

def analyse_weather_risk(weather_data):
    #identifying forecast based weather indicators
    forecast = weather_data["forecast"]
    risks=[]
    next_24h = forecast[:8]

    total_rain=0.0
    max_rain_3h =0.0
    max_rain_prob = None
    max_temp = None

    for entry in next_24h:
        rain=entry.get("rain",{})
        rain_amt=rain.get("3h",0) if isinstance(rain,dict) else 0
        total_rain+=rain_amt or 0
        max_rain_3h = max(max_rain_3h, rain_amt or 0)

        probability = entry.get("pop")
        if probability is not None:
            probability = probability*100
            if(max_rain_prob is None or probability>max_rain_prob):
                max_rain_prob = probability

        temp = entry.get("main",{}).get("temp")
        if temp is not None:
            temp_c = temp-273.15
            if max_temp is None or temp_c > max_temp:
                max_temp=temp_c
    if max_rain_3h>=7.5:
        risks.append("High Rainfall Indicator: Substantial rain is forecast within a 3-hour period.")
    if max_rain_prob is not None and max_rain_prob>=70:
        risks.append(f"High precipitation: UpTo {max_rain_prob:.0f}% in a forecast interval.")
    if max_temp is not None and max_temp>=35:
        risks.append("High Temperature indicator: Consider crop water needs and heat stress")

    if total_rain<1 and max_temp is not None and max_temp >=30:
        risks.append("Short Term Dry Weather indicator: Little rain is forecast alongside high temperature. But this is not a drought diagnosis")

    if not risks:
        risks.append("No major rainfall or heat indicators were detected by the current rule. But this not guarantee low risk")

    return {
        "risks":risks,
        "rain_next_24h_mm":round(total_rain,1),
        "max_rain_probability":(round(max_rain_prob) if max_rain_prob is not None else None)
    }

def generate_recommendations(suitability, risks):
    recommendations=[]
    if suitability["temperature"] >= 35:
        recommendations.append(
            "Check crop specific heat stress guidance and irrigation needs."
        )

    if suitability["humidity"] is not None and suitability["humidity"] >= 85:
        recommendations.append(
            "Monitor crops for humidity related disease favouring conditions."
        )

    if suitability["wind_speed"] >= 10:
        recommendations.append(
            "Check local wind warnings before spraying or other exposed work."
        )

    if risks["rain_next_24h_mm"] >= 15:
        recommendations.append(
            "Check field drainage and local rainfall warnings."
        )

    if not recommendations:
        recommendations.append(
            "Compare these weather conditions with the requirements of the crop being cultivated."
        )

    return recommendations

def show_agricultural_analysis(latitude, longitude):
    try:
        latitude=float(latitude)
        longitude=float(longitude)

        if not (-90 <= latitude <= 90):
            return
        if not (-180<= longitude <=180):
            return

        polygon=check_agri_relevance(latitude, longitude)
        if polygon is None:
            return
    # null typing
    except :
        return
'''
        weather_data=
        if weather_data is None:
          return
        
        suitability = calculate_suitability(weather_data)
        if suitability is None:
            return

        risks=analyse_weather_risk(weather_data)
        recommendations=generate_recommendations(suitability,risks)
'''
