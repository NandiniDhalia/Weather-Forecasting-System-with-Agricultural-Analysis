import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

from database import save_search
from weather_api import get_weather
from weather_processor import (
    get_recommendations,
    get_weather_description,
    create_temperature_chart,
    create_rainProb_chart,
    create_humidity_chart,
)
from agricultural_analysis import analyse_agriculture


def render_locked_feature(feature_name, description, button_key):
    """Display an access-control prompt when an unauthenticated visitor opens a restricted tab."""
    st.warning(f"🔒 **{feature_name}** is available only to authorised logged-in users.")
    st.write(description)
    if st.button("Log in / Create Account", type="primary", key=button_key):
        st.session_state["show_auth"] = True
        st.rerun()


def render_basic_weather(location, current, daily):
    """Level 1: Basic Weather current conditions, 7-day forecast, and general guidance."""
    description, icon = get_weather_description(current.get("weather_code"))

    st.subheader(f"Weather in {location['name']}, {location['country']}")
    st.caption(f"Updated at: {current.get('time', 'N/A')}")

    st.markdown(f"### {icon} {description}")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Temperature", f"{current.get('temperature_2m', 'N/A')} °C")
    col2.metric("Feels Like", f"{current.get('apparent_temperature', 'N/A')} °C")
    col3.metric("Humidity", f"{current.get('relative_humidity_2m', 'N/A')} %")
    col4.metric("Wind Speed", f"{current.get('wind_speed_10m', 'N/A')} km/h")

    col5, col6, col7 = st.columns(3)
    col5.metric("Pressure", f"{current.get('pressure_msl', 'N/A')} hPa")
    col6.metric("Wind Direction", f"{current.get('wind_direction_10m', 'N/A')} °")
    col7.metric("Current Precipitation", f"{current.get('precipitation', 0.0)} mm")

    st.divider()
    st.subheader("7-Day Forecast Summary")

    forecast_df = pd.DataFrame({
        "Date": daily["time"],
        "Weather": [get_weather_description(int(code))[1] for code in daily["weather_code"]],
        "Condition": [get_weather_description(int(code))[0] for code in daily["weather_code"]],
        "Max Temp (°C)": daily["temperature_2m_max"],
        "Min Temp (°C)": daily["temperature_2m_min"],
        "Precipitation (mm)": daily.get("precipitation_sum", [None] * len(daily["time"])),
        "Rain Probability (%)": daily["precipitation_probability_max"],
        "Max Wind (km/h)": daily["wind_speed_10m_max"],
    })
    st.dataframe(forecast_df, use_container_width=True, hide_index=True)

    st.divider()
    st.subheader("General Weather Recommendations")
    for rec in get_recommendations(current, daily):
        st.info(rec)


def render_advanced_weather(location, daily, hourly):
    """Level 2: Advanced Weather extended parameters and visual trend charts (Authorised users)."""
    st.subheader(f"Advanced Weather Trends — {location['name']}, {location['country']}")
    st.caption("7-day forecast visualisations and daily average atmospheric trends.")

    st.markdown("#### 7-Day Temperature Trends")
    temp_fig = create_temperature_chart(daily)
    st.pyplot(temp_fig)
    plt.close(temp_fig)

    st.markdown("#### Daily Precipitation Probability")
    rain_fig = create_rainProb_chart(daily)
    st.pyplot(rain_fig)
    plt.close(rain_fig)

    st.markdown("#### Daily Average Humidity Trend")
    humidity_fig = create_humidity_chart(hourly)
    st.pyplot(humidity_fig)
    plt.close(humidity_fig)


def render_agricultural_analysis(location, current, daily):
    """Level 3: Agricultural Analysis across all seven indicative indicators (Authorised users)."""
    st.subheader(f"Agricultural Analysis — {location['name']}, {location['country']}")

    agr_result = analyse_agriculture(location, current, daily)

    if not agr_result.get("available"):
        st.warning(
            agr_result.get(
                "reason",
                "Agricultural analysis is unavailable for the selected location."
            )
        )
        return

    profile = agr_result["location_profile"]
    indicators = agr_result["indicators"]

    p_col1, p_col2, p_col3 = st.columns(3)
    p_col1.metric("Agro-Climatic Zone", profile["agro_climatic_zone"])
    p_col2.metric("Primary Soil Type", profile["primary_soil_type"])
    p_col3.metric("Reference Weekly Rain", f"{profile['normal_weekly_rain_mm']} mm")

    st.divider()
    st.markdown("### 1. Weather-Related Agricultural Risks")

    risk_keys = ["heat_stress", "frost_risk", "drought_indicator", "excessive_rainfall"]
    r_cols = st.columns(2)
    for idx, key in enumerate(risk_keys):
        item = indicators[key]
        with r_cols[idx % 2]:
            with st.container(border=True):
                st.markdown(f"**{item['title']}** — `{item['level']}`")
                st.write(item["summary"])
                st.caption(f"Guidance: {item['guidance']}")
                st.caption(item["disclaimer"])

    st.divider()
    st.markdown("### 2. Agricultural Guidance Indicators")

    irrigation = indicators["irrigation_recommendation"]
    with st.container(border=True):
        st.markdown(f"**{irrigation['title']}** — `{irrigation['status']}`")
        st.write(irrigation["summary"])
        st.caption(f"Guidance: {irrigation['guidance']}")
        st.caption(irrigation["disclaimer"])

    soil = indicators["soil_moisture"]
    with st.container(border=True):
        st.markdown(
            f"**{soil['title']}** — `{soil['status']}` (Proxy Index: {soil['proxy_index']}/100)"
        )
        st.write(soil["summary"])
        st.caption(f"Guidance: {soil['guidance']}")
        st.caption(soil["disclaimer"])

    crop_section = indicators["crop_suitability"]
    st.markdown(f"#### {crop_section['title']}")
    crop_rows = [
        {
            "Crop": c["crop_name"],
            "Season": c["season"],
            "Suitability": c["rating"],
            "Score": f"{c['score']}/100",
            "Optimal Temp": c["optimal_temp_range"],
            "Optimal Humidity": c["optimal_humidity_range"],
            "Weekly Water Need (mm)": c["weekly_water_need_mm"],
            "Assessment Notes": c["details"],
        }
        for c in crop_section["crops"]
    ]
    st.dataframe(pd.DataFrame(crop_rows), use_container_width=True, hide_index=True)
    st.caption(crop_section["disclaimer"])


def view_page(city):
    """Render location search, validation, and role-based access across the three functional levels."""
    is_authenticated = bool(st.session_state.get("user"))

    if st.button("Get Weather", type="primary"):
        clean_city = city.strip()
        if not clean_city:
            st.warning("Please enter a city name.")
        elif len(clean_city) < 2 or not any(char.isalpha() for char in clean_city):
            st.warning("Please enter a valid city name.")
        else:
            try:
                with st.spinner("Fetching weather information..."):
                    result = get_weather(clean_city)
                    location = result["location"]
                    current = result["current"]

                    if clean_city.casefold() != location["name"].casefold():
                        st.error("City not found. Please enter the exact city name.")
                        st.session_state.pop("weather_result", None)
                    else:
                        if is_authenticated:
                            save_search(location, current, st.session_state["user"]["user_id"])
                        st.session_state["weather_result"] = result

            except ValueError as error:
                st.error(str(error))
                st.session_state.pop("weather_result", None)
            except Exception:
                st.error(
                    "Unable to retrieve weather information. Check your internet connection and try again later."
                )
                st.session_state.pop("weather_result", None)

    if "weather_result" in st.session_state:
        result = st.session_state["weather_result"]
        location = result["location"]
        current = result["current"]
        daily = result["daily"]
        hourly = result["hourly"]

        tab_basic, tab_advanced, tab_agri = st.tabs([
            "Basic Weather",
            "Advanced Weather",
            "Agricultural Analysis",
        ])

        with tab_basic:
            render_basic_weather(location, current, daily)

        with tab_advanced:
            if is_authenticated:
                render_advanced_weather(location, daily, hourly)
            else:
                render_locked_feature(
                    "Advanced Weather",
                    "Sign in with your username to view 7-day temperature charts, precipitation probability graphs, and daily humidity trends.",
                    button_key="unlock_advanced_btn",
                )

        with tab_agri:
            if is_authenticated:
                render_agricultural_analysis(location, current, daily)
            else:
                render_locked_feature(
                    "Agricultural Analysis",
                    "Sign in with your username to access indicative heat-stress, frost, drought, and excessive-rainfall risks, irrigation recommendations, crop suitability, and soil-moisture estimates.",
                    button_key="unlock_agri_btn",
                )
    else:
        st.info("Enter a valid city name (e.g., New Delhi, Pune, Ludhiana) and click 'Get Weather' to begin.")
