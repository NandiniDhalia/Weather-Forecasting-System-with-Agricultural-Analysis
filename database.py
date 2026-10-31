import sqlite3
from pathlib import Path
from datetime import datetime

database_path = Path(__file__).resolve().parent / "weather.db"

def get_connection():
    """Create a connection to the SQLite database."""
    conn = sqlite3.connect(database_path)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def initialize_database():
    """Create search history table if it doesn't exist."""
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS search_history( 
            search_id INTEGER PRIMARY KEY AUTOINCREMENT,
            city TEXT NOT NULL,
            country TEXT,
            temperature REAL,
            humidity REAL,
            weather_code INTEGER,
            searched_at TEXT NOT NULL)
        """)


def save_search(location,current):
    """Save a successful weather search."""
    with get_connection() as conn:
        conn.execute("""
            INSERT INTO search_history (city, country, temperature, humidity, weather_code, searched_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            location["name"],
            location["country"],
            current["temperature_2m"],
            current["relative_humidity_2m"],
            current["weather_code"],
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ))

def get_search_history(limit=50):
    """Retrieve search history."""
    with get_connection() as conn:
        cursor = conn.execute("""
            SELECT city, country, temperature, humidity, weather_code, searched_at
            FROM search_history
            ORDER BY searched_at DESC
            LIMIT ?
        """, (limit,))

        columns = [description[0] for description in cursor.description]

        return[dict(zip(columns, row)) for row in cursor.fetchall()]

def clear_search_history():
    """Delete all search history records."""
    with get_connection() as conn:
        conn.execute("DELETE FROM search_history")