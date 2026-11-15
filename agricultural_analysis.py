from agricultural_database import initialize_agr_database, get_agricultural_location


def _valid_floats(values):
    """Safely extract non-None numeric values as floats."""
    if not isinstance(values, list):
        return []
    cleaned = []
    for val in values:
        if val is not None:
            try:
                cleaned.append(float(val))
            except (TypeError, ValueError):
                continue
    return cleaned


def _normalize_temp_c(temp_value):
    """Convert temperature to Celsius if provided in Kelvin."""
    temp_c = float(temp_value)
    if temp_c > 100:
        temp_c -= 273.15
    return temp_c


def check_agr_relevance(city, state=None, country=None):
    """
    Check whether the location exists in the local agricultural reference database (agr_loc.db).
    """
    initialize_agr_database()
    ref = get_agricultural_location(city=city, state=state, country=country)
    if not ref:
        return None
    return ref


def assess_heat_stress(current_temp_c, humidity, max_temps):
    """Indicator 1: Indicative Heat Stress Risk."""
    peak_temp = max(max_temps) if max_temps else current_temp_c
    effective_temp = max(current_temp_c, peak_temp)

    if effective_temp >= 38.0 or (effective_temp >= 35.0 and humidity is not None and humidity >= 65.0):
        level = "High"
        summary = (
            f"Peak forecast temperature reaches {effective_temp:.1f} °C"
            + (f" with {humidity:.0f}% relative humidity" if humidity is not None else "")
            + ", indicating elevated thermal stress risk."
        )
        guidance = (
            "Consider light, frequent irrigation during cooler morning or evening hours "
            "and monitor heat-sensitive crops for wilting."
        )
    elif effective_temp >= 33.0:
        level = "Moderate"
        summary = f"Temperatures up to {effective_temp:.1f} °C may cause mild daytime heat stress."
        guidance = "Ensure adequate soil moisture before peak afternoon temperatures."
    else:
        level = "Low"
        summary = f"Current ({current_temp_c:.1f} °C) and forecast peak ({effective_temp:.1f} °C) temperatures are within manageable thermal limits."
        guidance = "No immediate heat-stress mitigation required."

    return {
        "title": "Heat Stress Risk",
        "category": "Weather-Related Risk",
        "level": level,
        "peak_temp_c": round(effective_temp, 1),
        "summary": summary,
        "guidance": guidance,
        "disclaimer": "Indicative weather-based heat assessment; crop tolerance varies by growth stage."
    }


def assess_frost_risk(current_temp_c, min_temps):
    """Indicator 2: Indicative Frost Risk."""
    lowest_temp = min(min_temps) if min_temps else current_temp_c
    effective_min = min(current_temp_c, lowest_temp)

    if effective_min <= 2.0:
        level = "High"
        summary = f"Minimum forecast temperature drops to {effective_min:.1f} °C, creating a strong possibility of ground or crop frost."
        guidance = "Protect frost-sensitive seedlings and vegetables using mulching, row covers, or light evening irrigation."
    elif effective_min <= 6.0:
        level = "Moderate"
        summary = f"Minimum forecast temperature reaches {effective_min:.1f} °C; localized cold stress is possible in low-lying fields."
        guidance = "Monitor overnight minimum temperature alerts for cold-sensitive crops."
    else:
        level = "Low"
        summary = f"Minimum forecast temperature ({effective_min:.1f} °C) remains well above freezing thresholds."
        guidance = "No frost precautions required based on current forecast."

    return {
        "title": "Frost Risk",
        "category": "Weather-Related Risk",
        "level": level,
        "min_temp_c": round(effective_min, 1),
        "summary": summary,
        "guidance": guidance,
        "disclaimer": "Indicative frost risk based on forecast air temperatures; microclimate conditions may vary."
    }


def assess_drought_indicator(rain_7d_mm, max_rain_prob, current_temp_c, normal_weekly_rain_mm):
    """Indicator 3: Indicative Weather-Based Drought Indicator."""
    baseline = float(normal_weekly_rain_mm) if normal_weekly_rain_mm else 18.0
    rain_ratio = rain_7d_mm / baseline if baseline > 0 else 0.0

    if rain_7d_mm < 2.0 and (max_rain_prob is None or max_rain_prob < 25) and current_temp_c >= 32.0:
        level = "High"
        summary = (
            f"Minimal 7-day forecast rainfall ({rain_7d_mm:.1f} mm vs. {baseline:.1f} mm regional weekly reference) "
            f"combined with warm conditions ({current_temp_c:.1f} °C) indicates pronounced dry conditions."
        )
        guidance = "Prioritize water conservation, mulching to reduce evaporation, and scheduled irrigation."
    elif rain_ratio < 0.40 and rain_7d_mm < 8.0:
        level = "Moderate"
        summary = (
            f"7-day forecast rainfall ({rain_7d_mm:.1f} mm) is below the regional reference ({baseline:.1f} mm), "
            "indicating developing dry weather."
        )
        guidance = "Plan supplemental irrigation depending on crop stage and soil water retention."
    else:
        level = "Low"
        summary = f"Forecast 7-day precipitation ({rain_7d_mm:.1f} mm) does not indicate immediate dry-spell stress."
        guidance = "Continue standard moisture monitoring."

    return {
        "title": "Drought Indicator",
        "category": "Weather-Related Risk",
        "level": level,
        "forecast_7d_rain_mm": round(rain_7d_mm, 1),
        "reference_weekly_rain_mm": round(baseline, 1),
        "summary": summary,
        "guidance": guidance,
        "disclaimer": "Note: This is a weather-based indicative drought assessment, not an official drought declaration."
    }


def assess_excessive_rainfall(precip_sums, max_rain_prob):
    """Indicator 4: Indicative Excessive Rainfall & Waterlogging Risk."""
    max_daily_rain = max(precip_sums) if precip_sums else 0.0
    total_3d_rain = sum(precip_sums[:3]) if precip_sums else 0.0

    if max_daily_rain >= 50.0 or total_3d_rain >= 90.0:
        level = "High"
        summary = (
            f"Heavy rainfall is forecast (up to {max_daily_rain:.1f} mm in a single day; "
            f"{total_3d_rain:.1f} mm over 3 days), increasing waterlogging risk."
        )
        guidance = "Clear field drainage channels, avoid fertilizer application before heavy rain, and safeguard harvested produce."
    elif max_daily_rain >= 25.0 or (max_rain_prob is not None and max_rain_prob >= 75 and total_3d_rain >= 35.0):
        level = "Moderate"
        summary = (
            f"Moderate-to-heavy rainfall ({max_daily_rain:.1f} mm peak daily; "
            f"{total_3d_rain:.1f} mm over 3 days) may cause temporary surface ponding."
        )
        guidance = "Inspect field bunds and drainage outlets in low-lying plots."
    else:
        level = "Low"
        summary = f"Forecast daily rainfall peak ({max_daily_rain:.1f} mm) is within normal drainage capacity."
        guidance = "No excessive-rainfall precautions needed."

    return {
        "title": "Excessive Rainfall Risk",
        "category": "Weather-Related Risk",
        "level": level,
        "max_daily_rain_mm": round(max_daily_rain, 1),
        "rain_next_3d_mm": round(total_3d_rain, 1),
        "summary": summary,
        "guidance": guidance,
        "disclaimer": "Indicative rainfall assessment based on forecast precipitation volumes."
    }


def generate_irrigation_guidance(rain_next_24h_mm, rain_next_3d_mm, current_temp_c, humidity, agr_ref):
    """Indicator 5: Indicative Irrigation Recommendations."""
    soil_type = agr_ref.get("primary_soil_type", "Regional Soil")
    retention = float(agr_ref.get("water_retention_factor", 0.6))

    if rain_next_24h_mm >= 10.0 or rain_next_3d_mm >= 25.0:
        action = "Defer / Reduce Irrigation"
        summary = (
            f"Significant rainfall is expected ({rain_next_24h_mm:.1f} mm in 24h; {rain_next_3d_mm:.1f} mm over 3 days). "
            "Additional irrigation is generally unnecessary and may risk over-watering."
        )
        guidance = "Hold scheduled irrigation and reassess soil moisture after rainfall."
    elif current_temp_c >= 33.0 and (humidity is None or humidity < 55.0) and rain_next_3d_mm < 5.0:
        action = "Increase / Supplemental Irrigation"
        retention_note = (
            "lower water retention in sandy/loamy soils accelerates drying"
            if retention < 0.60
            else "high evaporative demand depletes surface moisture"
        )
        summary = (
            f"Warm ({current_temp_c:.1f} °C), dry air with minimal 3-day rain ({rain_next_3d_mm:.1f} mm) "
            f"increases crop water demand; {retention_note} ({soil_type})."
        )
        guidance = "Apply supplemental irrigation during early morning or late evening to minimize evaporation losses."
    else:
        action = "Normal Scheduled Irrigation"
        summary = (
            f"Moderate weather conditions ({current_temp_c:.1f} °C, {rain_next_3d_mm:.1f} mm 3-day forecast rain) "
            f"on {soil_type} support standard crop irrigation intervals."
        )
        guidance = "Follow regular crop-stage irrigation schedules while checking topsoil moisture."

    return {
        "title": "Irrigation Recommendations",
        "category": "Agricultural Guidance",
        "status": action,
        "rain_next_24h_mm": round(rain_next_24h_mm, 1),
        "rain_next_3d_mm": round(rain_next_3d_mm, 1),
        "summary": summary,
        "guidance": guidance,
        "disclaimer": "Indicative weather-based irrigation guidance; verify field soil moisture before irrigating."
    }


def evaluate_crop_suitability(current_temp_c, humidity, rain_7d_mm, crops):
    """Indicator 6: Indicative Crop-Weather Suitability against local reference ranges."""
    evaluations = []

    for crop in crops:
        reasons = []
        score = 100

        min_t = float(crop["min_temp_c"])
        opt_min_t = float(crop["optimal_min_temp_c"])
        opt_max_t = float(crop["optimal_max_temp_c"])
        max_t = float(crop["max_temp_c"])

        if current_temp_c < min_t or current_temp_c > max_t:
            score -= 50
            reasons.append(
                f"Temperature ({current_temp_c:.1f} °C) is outside survival range ({min_t:.0f}–{max_t:.0f} °C)."
            )
        elif not (opt_min_t <= current_temp_c <= opt_max_t):
            score -= 20
            reasons.append(
                f"Temperature ({current_temp_c:.1f} °C) is outside optimal range ({opt_min_t:.0f}–{opt_max_t:.0f} °C)."
            )
        else:
            reasons.append(
                f"Temperature ({current_temp_c:.1f} °C) is within optimal range ({opt_min_t:.0f}–{opt_max_t:.0f} °C)."
            )

        if humidity is not None:
            opt_min_h = float(crop["optimal_min_humidity"])
            opt_max_h = float(crop["optimal_max_humidity"])
            if humidity < opt_min_h - 15 or humidity > opt_max_h + 15:
                score -= 25
                reasons.append(
                    f"Humidity ({humidity:.0f}%) diverges from optimal range ({opt_min_h:.0f}–{opt_max_h:.0f}%)."
                )
            elif not (opt_min_h <= humidity <= opt_max_h):
                score -= 10
                reasons.append(
                    f"Humidity ({humidity:.0f}%) is slightly outside optimal range ({opt_min_h:.0f}–{opt_max_h:.0f}%)."
                )

        weekly_need = float(crop["weekly_water_need_mm"])
        if rain_7d_mm < weekly_need * 0.35:
            reasons.append(
                f"7-day rain ({rain_7d_mm:.1f} mm) is below weekly water need ({weekly_need:.0f} mm); irrigation needed."
            )

        if score >= 80:
            rating = "Highly Suitable"
        elif score >= 55:
            rating = "Moderately Suitable"
        else:
            rating = "Unfavourable"

        evaluations.append({
            "crop_name": crop["crop_name"],
            "season": crop["season"],
            "rating": rating,
            "score": max(0, score),
            "optimal_temp_range": f"{opt_min_t:.0f}–{opt_max_t:.0f} °C",
            "optimal_humidity_range": f"{float(crop['optimal_min_humidity']):.0f}–{float(crop['optimal_max_humidity']):.0f}%",
            "weekly_water_need_mm": weekly_need,
            "details": " ".join(reasons)
        })

    return {
        "title": "Crop-Weather Suitability",
        "category": "Agricultural Guidance",
        "crops": evaluations,
        "disclaimer": (
            "Indicative weather-based comparison against crop reference ranges; "
            "does not represent a complete agronomic or soil-fertility evaluation."
        )
    }


def estimate_soil_moisture(current_precip_mm, rain_next_3d_mm, current_temp_c, humidity, agr_ref):
    """Indicator 7: Proxy-Based Soil-Moisture Assessment."""
    soil_type = agr_ref.get("primary_soil_type", "Regional Soil")
    retention = float(agr_ref.get("water_retention_factor", 0.6))

    # Proxy moisture index (0 to 100 scale) derived from precipitation, retention, humidity, and temperature
    moisture_index = 45.0 * retention + 20.0
    moisture_index += min(30.0, (current_precip_mm * 3.0) + (rain_next_3d_mm * 0.8))

    if humidity is not None:
        moisture_index += (humidity - 50.0) * 0.20

    if current_temp_c > 25.0:
        moisture_index -= (current_temp_c - 25.0) * 1.1

    moisture_index = max(5.0, min(95.0, moisture_index))

    if moisture_index >= 68.0:
        status = "Wet / High Moisture"
        summary = (
            f"Estimated proxy moisture index is {moisture_index:.0f}/100 on {soil_type}, "
            "reflecting recent/expected precipitation and moderate evaporation."
        )
        guidance = "Avoid over-irrigation and monitor drainage in heavy-textured soils."
    elif moisture_index >= 40.0:
        status = "Moderate / Adequate"
        summary = (
            f"Estimated proxy moisture index is {moisture_index:.0f}/100 on {soil_type}, "
            "indicating balanced topsoil moisture conditions."
        )
        guidance = "Maintain normal crop monitoring and scheduled irrigation."
    else:
        status = "Dry / Low Moisture"
        summary = (
            f"Estimated proxy moisture index is {moisture_index:.0f}/100 on {soil_type}, "
            "driven by warm temperatures, low rainfall, and soil drainage characteristics."
        )
        guidance = "Check root-zone moisture physically and plan timely irrigation."

    return {
        "title": "Soil-Moisture Assessment",
        "category": "Agricultural Guidance",
        "status": status,
        "proxy_index": round(moisture_index),
        "soil_type": soil_type,
        "summary": summary,
        "guidance": guidance,
        "disclaimer": (
            "Limitation: This is an indirect proxy estimate derived from weather inputs and regional soil reference data, "
            "not a direct physical soil-sensor measurement."
        )
    }


def analyse_agriculture(location_data, weather_data, forecast_data=None):
    """
    Main entry point for Module 4 (Agricultural Analysis).
    Combines external weather observations/forecasts with local SQLite reference data (agr_loc.db).
    """
    if not isinstance(location_data, dict) or not isinstance(weather_data, dict):
        return {
            "available": False,
            "reason": "Missing location or current weather information."
        }

    city = location_data.get("name", "")
    state = location_data.get("admin1", "")
    country = location_data.get("country", "")

    agr_ref = check_agr_relevance(city=city, state=state, country=country)
    if not agr_ref:
        return {
            "available": False,
            "reason": (f"Agricultural reference data is not available for '{city}'. Agricultural analysis is limited to supported agriculture-relevant locations.")
        }

    raw_temp = weather_data.get("temperature_2m")
    if raw_temp is None:
        return {
            "available": False,
            "reason": "Current temperature data is unavailable for agricultural calculations."
        }

    current_temp_c = _normalize_temp_c(raw_temp)
    humidity = (
        float(weather_data["relative_humidity_2m"])
        if weather_data.get("relative_humidity_2m") is not None
        else None
    )
    current_precip_mm = (
        float(weather_data["precipitation"])
        if weather_data.get("precipitation") is not None
        else 0.0
    )

    daily = forecast_data if isinstance(forecast_data, dict) else {}
    max_temps = _valid_floats(daily.get("temperature_2m_max", []))
    min_temps = _valid_floats(daily.get("temperature_2m_min", []))
    precip_sums = _valid_floats(daily.get("precipitation_sum", []))
    rain_probs = _valid_floats(daily.get("precipitation_probability_max", []))

    max_rain_prob = max(rain_probs) if rain_probs else None
    rain_next_24h_mm = precip_sums[0] if precip_sums else current_precip_mm
    rain_next_3d_mm = sum(precip_sums[:3]) if precip_sums else current_precip_mm
    rain_7d_mm = sum(precip_sums) if precip_sums else current_precip_mm

    indicators = {
        "heat_stress": assess_heat_stress(current_temp_c, humidity, max_temps),
        "frost_risk": assess_frost_risk(current_temp_c, min_temps),
        "drought_indicator": assess_drought_indicator(
            rain_7d_mm, max_rain_prob, current_temp_c, agr_ref.get("normal_weekly_rain_mm")
        ),
        "excessive_rainfall": assess_excessive_rainfall(precip_sums, max_rain_prob),
        "irrigation_recommendation": generate_irrigation_guidance(
            rain_next_24h_mm, rain_next_3d_mm, current_temp_c, humidity, agr_ref
        ),
        "crop_suitability": evaluate_crop_suitability(
            current_temp_c, humidity, rain_7d_mm, agr_ref.get("crops", [])
        ),
        "soil_moisture": estimate_soil_moisture(
            current_precip_mm, rain_next_3d_mm, current_temp_c, humidity, agr_ref
        )
    }

    return {
        "available": True,
        "location_profile": {
            "city": agr_ref["city"],
            "state": agr_ref["state"],
            "agro_climatic_zone": agr_ref["agro_climatic_zone"],
            "primary_soil_type": agr_ref["primary_soil_type"],
            "normal_weekly_rain_mm": agr_ref["normal_weekly_rain_mm"]
        },
        "indicators": indicators
    }