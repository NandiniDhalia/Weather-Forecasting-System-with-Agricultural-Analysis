import sqlite3
from pathlib import Path

AGR_DB_PATH = Path(__file__).resolve().parent / "agr_loc.db"


def get_agr_connection():
    """Create a connection to the local agricultural reference SQLite database."""
    conn = sqlite3.connect(AGR_DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def initialize_agr_database():
    """Create tables in agr_loc.db and populate baseline Indian agricultural reference data."""
    with get_agr_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS agricultural_locations (
                location_id INTEGER PRIMARY KEY AUTOINCREMENT,
                city TEXT NOT NULL COLLATE NOCASE,
                state TEXT NOT NULL COLLATE NOCASE,
                country TEXT NOT NULL DEFAULT 'India' COLLATE NOCASE,
                agro_climatic_zone TEXT NOT NULL,
                primary_soil_type TEXT NOT NULL,
                water_retention_factor REAL NOT NULL,
                normal_weekly_rain_mm REAL NOT NULL,
                UNIQUE(city, state, country)
            )
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS crop_references (
                crop_id INTEGER PRIMARY KEY AUTOINCREMENT,
                crop_name TEXT NOT NULL UNIQUE COLLATE NOCASE,
                season TEXT NOT NULL,
                min_temp_c REAL NOT NULL,
                optimal_min_temp_c REAL NOT NULL,
                optimal_max_temp_c REAL NOT NULL,
                max_temp_c REAL NOT NULL,
                optimal_min_humidity REAL NOT NULL,
                optimal_max_humidity REAL NOT NULL,
                weekly_water_need_mm REAL NOT NULL
            )
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS location_crops (
                location_id INTEGER NOT NULL,
                crop_id INTEGER NOT NULL,
                PRIMARY KEY (location_id, crop_id),
                FOREIGN KEY (location_id) REFERENCES agricultural_locations(location_id) ON DELETE CASCADE,
                FOREIGN KEY (crop_id) REFERENCES crop_references(crop_id) ON DELETE CASCADE
            )
        """)

        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_agr_city ON agricultural_locations(city)
        """)

        _seed_reference_data(conn)


def _seed_reference_data(conn):
    """Idempotently seed crop reference ranges and Indian agricultural locations."""
    crops = [
        # (crop_name, season, min_temp, opt_min_temp, opt_max_temp, max_temp, opt_min_hum, opt_max_hum, weekly_water_mm)
        ("Wheat", "Rabi", 4.0, 15.0, 25.0, 32.0, 45.0, 70.0, 25.0),
        ("Rice (Paddy)", "Kharif", 15.0, 22.0, 32.0, 38.0, 65.0, 85.0, 55.0),
        ("Maize", "Kharif / Rabi", 10.0, 18.0, 30.0, 36.0, 50.0, 75.0, 32.0),
        ("Mustard", "Rabi", 3.0, 12.0, 25.0, 30.0, 40.0, 65.0, 18.0),
        ("Chickpea (Chana)", "Rabi", 5.0, 15.0, 26.0, 32.0, 40.0, 65.0, 15.0),
        ("Cotton", "Kharif", 15.0, 22.0, 34.0, 40.0, 50.0, 75.0, 35.0),
        ("Sugarcane", "Annual", 12.0, 22.0, 34.0, 40.0, 60.0, 80.0, 48.0),
        ("Soybean", "Kharif", 12.0, 20.0, 30.0, 36.0, 55.0, 75.0, 30.0),
        ("Groundnut", "Kharif", 14.0, 22.0, 32.0, 37.0, 50.0, 75.0, 28.0),
        ("Potato", "Rabi", 4.0, 14.0, 22.0, 28.0, 55.0, 80.0, 26.0),
        ("Onion", "Rabi / Kharif", 8.0, 15.0, 28.0, 35.0, 45.0, 70.0, 24.0),
        ("Tomato", "Year-round", 10.0, 18.0, 29.0, 35.0, 50.0, 75.0, 28.0),
        ("Bajra (Pearl Millet)", "Kharif", 14.0, 24.0, 35.0, 42.0, 35.0, 65.0, 18.0),
        ("Jowar (Sorghum)", "Kharif / Rabi", 12.0, 22.0, 33.0, 40.0, 40.0, 70.0, 20.0),
    ]

    conn.executemany("""
        INSERT OR IGNORE INTO crop_references (
            crop_name, season, min_temp_c, optimal_min_temp_c, optimal_max_temp_c,
            max_temp_c, optimal_min_humidity, optimal_max_humidity, weekly_water_need_mm
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, crops)

    locations = [
        # (city, state, country, agro_climatic_zone, primary_soil_type, water_retention_factor, normal_weekly_rain_mm)
        ("New Delhi", "Delhi", "India", "Trans-Gangetic Plains", "Alluvial Sandy Loam", 0.55, 16.0),
        ("Ludhiana", "Punjab", "India", "Trans-Gangetic Plains", "Alluvial Loam", 0.65, 18.0),
        ("Amritsar", "Punjab", "India", "Trans-Gangetic Plains", "Alluvial Loam", 0.65, 17.0),
        ("Karnal", "Haryana", "India", "Trans-Gangetic Plains", "Alluvial Clay Loam", 0.68, 17.0),
        ("Hisar", "Haryana", "India", "Trans-Gangetic Plains", "Sandy Loam", 0.48, 12.0),
        ("Jaipur", "Rajasthan", "India", "Western Dry Region", "Arid Sandy Soil", 0.40, 12.0),
        ("Jodhpur", "Rajasthan", "India", "Western Dry Region", "Desert Sandy Soil", 0.35, 8.0),
        ("Lucknow", "Uttar Pradesh", "India", "Upper Gangetic Plains", "Alluvial Loam", 0.65, 22.0),
        ("Kanpur", "Uttar Pradesh", "India", "Upper Gangetic Plains", "Alluvial Loam", 0.64, 20.0),
        ("Meerut", "Uttar Pradesh", "India", "Upper Gangetic Plains", "Alluvial Loam", 0.66, 20.0),
        ("Agra", "Uttar Pradesh", "India", "Upper Gangetic Plains", "Sandy Loam", 0.52, 16.0),
        ("Varanasi", "Uttar Pradesh", "India", "Middle Gangetic Plains", "Alluvial Silt Loam", 0.68, 24.0),
        ("Patna", "Bihar", "India", "Middle Gangetic Plains", "Alluvial Silt Loam", 0.70, 26.0),
        ("Kolkata", "West Bengal", "India", "Lower Gangetic Plains", "Alluvial Clayey Loam", 0.75, 34.0),
        ("Guwahati", "Assam", "India", "Eastern Himalayan Region", "Alluvial & Red Loam", 0.74, 42.0),
        ("Bhopal", "Madhya Pradesh", "India", "Central Plateau & Hills", "Medium Black Soil", 0.72, 24.0),
        ("Indore", "Madhya Pradesh", "India", "Central Plateau & Hills", "Deep Black Cotton Soil", 0.76, 22.0),
        ("Nagpur", "Maharashtra", "India", "Central Plateau & Hills", "Black Cotton Soil", 0.75, 24.0),
        ("Pune", "Maharashtra", "India", "Western Plateau & Hills", "Medium Black Soil", 0.68, 20.0),
        ("Nashik", "Maharashtra", "India", "Western Plateau & Hills", "Black & Red Soil", 0.65, 18.0),
        ("Kolhapur", "Maharashtra", "India", "Western Plateau & Hills", "Red & Lateritic Loam", 0.70, 28.0),
        ("Ahmedabad", "Gujarat", "India", "Gujarat Plains & Hills", "Alluvial Sandy Loam", 0.52, 16.0),
        ("Rajkot", "Gujarat", "India", "Gujarat Plains & Hills", "Medium Black Soil", 0.64, 15.0),
        ("Surat", "Gujarat", "India", "Gujarat Plains & Hills", "Deep Black Alluvial", 0.72, 28.0),
        ("Hyderabad", "Telangana", "India", "Southern Plateau & Hills", "Red Sandy Loam", 0.56, 19.0),
        ("Warangal", "Telangana", "India", "Southern Plateau & Hills", "Red & Black Soil", 0.62, 21.0),
        ("Bengaluru", "Karnataka", "India", "Southern Plateau & Hills", "Red Loamy Soil", 0.58, 20.0),
        ("Mysuru", "Karnataka", "India", "Southern Plateau & Hills", "Red Sandy Loam", 0.60, 19.0),
        ("Chennai", "Tamil Nadu", "India", "East Coast Plains & Hills", "Coastal Alluvial & Red", 0.60, 26.0),
        ("Coimbatore", "Tamil Nadu", "India", "Southern Plateau & Hills", "Red Loam & Black Soil", 0.62, 16.0),
    ]

    conn.executemany("""
        INSERT OR IGNORE INTO agricultural_locations (
            city, state, country, agro_climatic_zone,
            primary_soil_type, water_retention_factor, normal_weekly_rain_mm
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
    """, locations)

    crop_rows = conn.execute("SELECT crop_id, crop_name FROM crop_references").fetchall()
    crop_map = {row["crop_name"]: row["crop_id"] for row in crop_rows}

    loc_rows = conn.execute("SELECT location_id, city FROM agricultural_locations").fetchall()
    loc_map = {row["city"]: row["location_id"] for row in loc_rows}

    city_crop_links = {
        "New Delhi": ["Wheat", "Mustard", "Potato", "Tomato", "Bajra (Pearl Millet)"],
        "Ludhiana": ["Wheat", "Rice (Paddy)", "Maize", "Potato"],
        "Amritsar": ["Wheat", "Rice (Paddy)", "Potato", "Maize"],
        "Karnal": ["Wheat", "Rice (Paddy)", "Sugarcane", "Mustard"],
        "Hisar": ["Wheat", "Mustard", "Cotton", "Bajra (Pearl Millet)", "Chickpea (Chana)"],
        "Jaipur": ["Bajra (Pearl Millet)", "Mustard", "Wheat", "Chickpea (Chana)"],
        "Jodhpur": ["Bajra (Pearl Millet)", "Jowar (Sorghum)", "Mustard"],
        "Lucknow": ["Wheat", "Rice (Paddy)", "Sugarcane", "Potato", "Mustard"],
        "Kanpur": ["Wheat", "Rice (Paddy)", "Potato", "Chickpea (Chana)"],
        "Meerut": ["Sugarcane", "Wheat", "Rice (Paddy)", "Potato"],
        "Agra": ["Potato", "Wheat", "Mustard", "Bajra (Pearl Millet)"],
        "Varanasi": ["Rice (Paddy)", "Wheat", "Chickpea (Chana)", "Tomato"],
        "Patna": ["Rice (Paddy)", "Wheat", "Maize", "Potato"],
        "Kolkata": ["Rice (Paddy)", "Potato", "Tomato"],
        "Guwahati": ["Rice (Paddy)", "Potato", "Tomato", "Mustard"],
        "Bhopal": ["Soybean", "Wheat", "Chickpea (Chana)", "Maize"],
        "Indore": ["Soybean", "Wheat", "Chickpea (Chana)", "Onion"],
        "Nagpur": ["Cotton", "Soybean", "Jowar (Sorghum)", "Chickpea (Chana)"],
        "Pune": ["Sugarcane", "Onion", "Jowar (Sorghum)", "Tomato"],
        "Nashik": ["Onion", "Tomato", "Wheat", "Maize"],
        "Kolhapur": ["Sugarcane", "Rice (Paddy)", "Groundnut", "Soybean"],
        "Ahmedabad": ["Cotton", "Wheat", "Groundnut", "Bajra (Pearl Millet)"],
        "Rajkot": ["Groundnut", "Cotton", "Wheat", "Chickpea (Chana)"],
        "Surat": ["Sugarcane", "Rice (Paddy)", "Cotton"],
        "Hyderabad": ["Rice (Paddy)", "Maize", "Cotton", "Jowar (Sorghum)"],
        "Warangal": ["Cotton", "Rice (Paddy)", "Maize"],
        "Bengaluru": ["Maize", "Tomato", "Onion", "Groundnut"],
        "Mysuru": ["Rice (Paddy)", "Sugarcane", "Maize", "Groundnut"],
        "Chennai": ["Rice (Paddy)", "Groundnut", "Sugarcane"],
        "Coimbatore": ["Cotton", "Maize", "Jowar (Sorghum)", "Groundnut"],
    }

    links_to_insert = []
    for city_name, crop_names in city_crop_links.items():
        loc_id = loc_map.get(city_name)
        if not loc_id:
            continue
        for c_name in crop_names:
            c_id = crop_map.get(c_name)
            if c_id:
                links_to_insert.append((loc_id, c_id))

    conn.executemany("""
        INSERT OR IGNORE INTO location_crops (location_id, crop_id)
        VALUES (?, ?)
    """, links_to_insert)


def get_agricultural_location(city, state=None, country=None):
    """
    Look up an agriculture-relevant location in agr_loc.db.
    Returns a dict with location metadata and matching crop reference rows, or None if unsupported.
    """
    if not isinstance(city, str) or not city.strip():
        return None

    clean_city = city.strip()

    with get_agr_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM agricultural_locations WHERE city = ? COLLATE NOCASE",
            (clean_city,)
        ).fetchall()

        if not rows:
            return None

        selected = rows[0]
        if state and isinstance(state, str) and state.strip():
            state_clean = state.strip().casefold()
            for row in rows:
                if row["state"].casefold() in state_clean or state_clean in row["state"].casefold():
                    selected = row
                    break

        crops = conn.execute("""
            SELECT c.*
            FROM crop_references c
            JOIN location_crops lc ON c.crop_id = lc.crop_id
            WHERE lc.location_id = ?
            ORDER BY c.crop_name ASC
        """, (selected["location_id"],)).fetchall()

        result = dict(selected)
        result["crops"] = [dict(c) for c in crops]
        return result


def list_supported_locations():
    """Return a sorted list of all supported city/state pairs in agr_loc.db."""
    with get_agr_connection() as conn:
        rows = conn.execute(
            "SELECT city, state, agro_climatic_zone FROM agricultural_locations ORDER BY city ASC"
        ).fetchall()
        return [dict(row) for row in rows]