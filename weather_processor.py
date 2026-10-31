import matplotlib.pyplot as plt
import pandas as pd

def create_temperature_chart(daily):

    dates = daily["time"]
    minimum = daily["temperature_2m_min"]
    maximum = daily["temperature_2m_max"]

    fig,ax = plt.subplots(figsize=(10, 4))

    ax.plot(dates, minimum, marker='o', label='Minimum Temperature (°C)', color='blue')

    ax.plot(dates, maximum, marker='o', label='Maximum Temperature (°C)', color='red')

    ax.set_title("7-Day Temperature Forecast")
    ax.set_xlabel("Date")
    ax.set_ylabel("Temperature (°C)")

    ax.legend()
    ax.grid(True, linestyle="--", alpha=0.5)

    plt.xticks(rotation=45)
    fig.tight_layout()

    return fig

def create_rainProb_chart(daily):
    dates = daily["time"]
    probabilities = daily["precipitation_probability_max"]

    fig,ax = plt.subplots(figsize=(10, 4))
    ax.bar(dates, probabilities)

    ax.set_title("Daily Probability of Precipitation")
    ax.set_xlabel("Date")
    ax.set_ylabel("Probability (%)")
    ax.set_ylim(0, 100)
    ax.grid(axis='y', linestyle="--", alpha=0.5)

    fig.autofmt_xdate()
    fig.tight_layout()

    return fig

def create_humidity_chart(hourly):
    humidity_df = pd.DataFrame({
        "time": pd.to_datetime(hourly["time"]),
        "humidity": hourly["relative_humidity_2m"]
    })

    humidity_df["date"] = humidity_df["time"].dt.date

    daily_humidity = humidity_df.groupby(
        "date"
    )["humidity"].mean()

    fig, ax = plt.subplots(figsize=(10, 4))

    ax.plot(
        daily_humidity.index.astype(str),
        daily_humidity.values,
        marker="o",
        label="Average Humidity"
    )

    ax.set_title("Daily Average Humidity Trend")
    ax.set_xlabel("Date")
    ax.set_ylabel("Humidity (%)")
    ax.set_ylim(0, 100)
    ax.legend()
    ax.grid(True, linestyle="--", alpha=0.5)

    fig.autofmt_xdate()
    fig.tight_layout()

    return fig

def get_recommendations(current, daily):
    recommendations = []

    temperature = current["temperature_2m"]
    wind_speed = current["wind_speed_10m"]
    humidity = current["relative_humidity_2m"]
    rain_probability = daily.get("precipitation_probability_max", [])
    if temperature >= 35:
        recommendations.append("High temperature: stay hydrated and limit outdoor activities.")
    elif temperature <= 10:
        recommendations.append("Low temperature: consider wearing warm clothing.")
    elif temperature >=28:
        recommendations.append("Warm conditions: consider light, breathable clothing.")

    valid_probabilities = [value for value in rain_probability if value is not None]

    if valid_probabilities and max(valid_probabilities) >= 60:
        recommendations.append("Rain is likely on at least one forecast day. Consider carrying an umbrella.")
    
    if wind_speed >= 30:
        recommendations.append("Strong winds are reported. Take care during outdoor activities.")
    
    if humidity >= 80:
        recommendations.append("High humidity: Stay hydrated and consider breathable clothing.")

    if not recommendations:
        recommendations.append("Weather conditions are generally favorable. Enjoy your day!")

    return recommendations


WEATHER_CODES = {
    0: ("Clear sky", "☀️"),
    1: ("Mainly clear", "🌤️"),
    2: ("Partly cloudy", "⛅"),
    3: ("Overcast", "☁️"),
    45: ("Fog", "🌫️"),
    48: ("Depositing rime fog", "🌫️"),
    51: ("Light drizzle", "🌦️"),
    53: ("Moderate drizzle", "🌦️"),
    55: ("Dense drizzle", "🌧️"),
    56: ("Light freezing drizzle", "🌧️"),
    57: ("Dense freezing drizzle", "🌧️"),
    61: ("Slight rain", "🌦️"),
    63: ("Moderate rain", "🌧️"),
    65: ("Heavy rain", "🌧️"),
    66: ("Light freezing rain", "🌧️"),
    67: ("Heavy freezing rain", "🌧️"),
    71: ("Slight snowfall", "🌨️"),
    73: ("Moderate snowfall", "❄️"),
    75: ("Heavy snowfall", "❄️"),
    77: ("Snow grains", "❄️"),
    80: ("Slight rain showers", "🌦️"),
    81: ("Moderate rain showers", "🌧️"),
    82: ("Violent rain showers", "🌧️"),
    85: ("Slight snow showers", "🌨️"),
    86: ("Heavy snow showers", "❄️"),
    95: ("Thunderstorm", "⛈️"),
    96: ("Thunderstorm with slight hail", "⛈️"),
    99: ("Thunderstorm with heavy hail", "⛈️")
}


def get_weather_description(code):
    """Return a readable description and icon for a weather code."""
    return WEATHER_CODES.get(
        code,
        ("Unknown weather condition", "🌡️")
    )

