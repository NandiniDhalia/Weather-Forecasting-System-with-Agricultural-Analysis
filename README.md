# Weather Forecasting System with Agricultural Analysis

An interactive web-based weather forecasting and agricultural decision-support application developed using **Python**, **Streamlit**, and **SQLite**. The system retrieves location-based current weather and 7-day forecast data, visualizes atmospheric trends, and translates weather parameters into indicative agricultural risk and guidance indicators using a local Indian agricultural reference database.

---

## Key Features & Functional Levels

### 1. Basic Weather (Public Access)
* **Location Search & Validation:** Validates city and Indian state inputs before displaying weather data to prevent false matches.
* **Current Weather Conditions:** Displays temperature, feels-like temperature, relative humidity, wind speed, wind direction, atmospheric pressure, precipitation, and weather condition icons.
* **7-Day Forecast Summary:** Tabular daily forecast with maximum/minimum temperatures, precipitation volume (`mm`), precipitation probability (`%`), and maximum wind speed.
* **General Weather Recommendations:** Actionable day-to-day advisories based on temperature, rainfall probability, humidity, and wind speed.

### 2. Advanced Weather (Authorised Users)
* **7-Day Temperature Trends:** Line chart comparing daily minimum and maximum forecast temperatures.
* **Daily Precipitation Probability:** Bar chart illustrating daily rainfall likelihood over the 7-day forecast window.
* **Daily Average Humidity Trend:** Aggregated daily humidity curve derived from hourly forecast records.

### 3. Agricultural Analysis (Authorised Users)
Combines real-time and forecast weather data with regional agro-climatic zone, soil type, and crop reference data stored locally in `agr_loc.db` to generate **seven indicative indicators**:

* **Weather-Related Agricultural Risks:**
  1. **Heat Stress Risk** – Evaluates high-temperature and humidity stress thresholds.
  2. **Frost Risk** – Assesses low minimum forecast temperatures for cold/frost sensitivity.
  3. **Drought Indicator** – Compares 7-day forecast rainfall against regional weekly reference rainfall.
  4. **Excessive Rainfall Risk** – Identifies heavy single-day or 3-day cumulative rainfall and potential waterlogging.
* **Agricultural Guidance Indicators:**
  5. **Irrigation Recommendations** – Suggests deferring, maintaining, or increasing irrigation based on forecast rain, temperature, humidity, and soil water retention.
  6. **Crop-Weather Suitability** – Evaluates region-specific crops against optimal temperature, humidity, and weekly water requirement ranges.
  7. **Soil-Moisture Assessment** – Estimates a proxy soil-moisture index (`0–100`) from precipitation, temperature, humidity, and soil retention characteristics.

### 4. Authentication & Personal Search History
* **Username-Based Accounts:** Secure registration and login using a unique username and PBKDF2-SHA256 salted password hashing (no email required).
* **Remember Me Persistence:** Supports 30-day persistent device sessions via secure hashed tokens.
* **User-Isolated Search History:** Saves valid location searches per account in `DD:MM:YYYY HH:MM:SS` (IST) format with one-click history clearing.

---

## Technology Stack

* **Language & Web Framework:** Python, Streamlit
* **Data Processing & Visualization:** Pandas, NumPy, Matplotlib
* **Relational Databases:** SQLite (`weather.db` for user accounts/search history; `agr_loc.db` for Indian agricultural locations and crop reference data)
* **External Data Integration:** Python `requests` over HTTPS for geocoding and weather forecast retrieval
* **Session & Environment Management:** `extra-streamlit-components`, `python-dotenv`

---

## Project Structure

```text
Weather-Forecasting-System/
│
├── main.py                     # Main Streamlit entry point, session/cookie handling, and search history UI
├── web_page.py                 # Dashboard views for Basic Weather, Advanced Weather, and Agricultural Analysis
├── weather_api.py              # Location validation and current/forecast weather data retrieval
├── weather_processor.py        # Weather condition mapping, general advisories, and Matplotlib trend charts
├── agricultural_analysis.py    # Calculation engine for all seven agricultural risk and guidance indicators
├── agricultural_database.py    # Local SQLite database (agr_loc.db) setup and Indian crop/location reference queries
├── database.py                 # Relational SQLite database (weather.db) for users, tokens, and search history
├── auth.py                     # Password hashing, user authentication, and remember-token management
├── auth_page.py                # Login and account creation UI tabs
├── requirements.txt            # Python dependencies
├── README.md                   # Project documentation
└── .env                        # Local environment variables (excluded from version control)
```

---

## Installation & Execution

1. **Clone or download the repository:**
   ```bash
   git clone <your-repository-url>
   cd "Weather Forecasting System with Agricultural Analysis"
   ```

2. **Install the required dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables (optional):**
   Create a `.env` file in the project root for any local configuration settings (do not commit `.env` to public repositories).

4. **Run the Streamlit application:**
   ```bash
   streamlit run main.py
   ```
   Both SQLite databases (`weather.db` and `agr_loc.db`) are created and initialized automatically on first launch.

---

## Limitations & Disclaimers

* Agricultural indicators (drought indicator, crop-weather suitability, and soil-moisture index) are **weather-based indicative estimates** derived from regional reference ranges, they are not direct physical soil-sensor measurements or official agronomic declarations.
* Forecast accuracy and coverage depend on the external weather data service, while agricultural analysis is limited to locations configured in `agr_loc.db`.