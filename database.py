import sqlite3
from pathlib import Path
from datetime import datetime, timedelta, timezone

database_path = Path(__file__).resolve().parent / "weather.db"

def get_connection():
    """Create a connection to the SQLite database."""
    conn = sqlite3.connect(database_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def initialize_database():
    """Create search history table if it doesn't exist."""
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE COLLATE NOCASE,
                password_hash TEXT NOT NULL,
                password_salt TEXT NOT NULL,
                created_at TEXT NOT NULL)
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS search_history( 
            search_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            city TEXT NOT NULL,
            country TEXT,
            temperature REAL,
            humidity REAL,
            weather_code INTEGER,
            searched_at TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
            )
        """)

        history_col = {row["name"] for row in conn.execute("PRAGMA table_info(search_history)").fetchall()}
        if "user_id" not in history_col:
            conn.execute("ALTER TABLE search_history ADD COLUMN user_id INTEGER REFERENCES users(user_id)")
        conn.execute("""
            CREATE TABLE IF NOT EXISTS remember_tokens ( token_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                token_hash TEXT NOT NULL UNIQUE,
                expires_at TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE)
        """)
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_history_user_date ON search_history(user_id, searched_at DESC)
        """)

def create_user(username, password_hash, password_salt):
    username = username.strip().lower()
    with get_connection() as conn:
        cursor = conn.execute(""" INSERT INTO users (username, password_hash, password_salt, created_at) VALUES (?, ?, ?, ?) """, (username, password_hash, password_salt, datetime.now(timezone.utc).isoformat()))
    return cursor.lastrowid

def get_user_by_username(username):
    with get_connection() as conn:
        row = conn.execute(
            "SELECT * FROM users WHERE username = ? COLLATE NOCASE",
            (username.strip(),)
        ).fetchone()
        return dict(row) if row else None


def get_user_by_id(user_id):
    with get_connection() as conn:
        row = conn.execute(
            "SELECT user_id, username, created_at FROM users WHERE user_id = ?",
            (user_id,)
        ).fetchone()
        return dict(row) if row else None

def save_search(location,current, user_id):
    """Save a successful weather search."""
    if user_id is None:
        return
    with get_connection() as conn:
        conn.execute("""
            INSERT INTO search_history (user_id, city, country, temperature, humidity, weather_code, searched_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            user_id,
            location.get("name", ""),
            location.get("country", ""),
            current.get("temperature_2m"),
            current.get("relative_humidity_2m"),
            current.get("weather_code"),
            datetime.now(timezone.utc).isoformat()
        ))

def get_search_history(user_id, limit=50):
    """Retrieve search history."""
    if user_id is None:
        return []
    with get_connection() as conn:
        rows = conn.execute("""
            SELECT city, country, temperature, humidity, weather_code, searched_at
            FROM search_history
            WHERE user_id = ?
            ORDER BY searched_at DESC
            LIMIT ?
        """, (user_id, limit)).fetchall()
        return [dict(row) for row in rows]


def clear_search_history(user_id):
    """Delete all search history records."""
    if user_id is None:
        return
    with get_connection() as conn:
        conn.execute("DELETE FROM search_history WHERE user_id = ?", (user_id,))

def save_remember_token(user_id, token_hash, expires_at):
    with get_connection() as conn:
        conn.execute("""
            INSERT INTO remember_tokens (user_id, token_hash, expires_at)
            VALUES (?, ?, ?)
        """, (user_id, token_hash, expires_at))


def get_user_by_remember_token(token_hash):
    now = datetime.now(timezone.utc).isoformat()
    with get_connection() as conn:
        row = conn.execute("""
            SELECT users.user_id, users.username
            FROM remember_tokens
            JOIN users ON users.user_id = remember_tokens.user_id
            WHERE remember_tokens.token_hash = ? AND remember_tokens.expires_at > ?
        """, (token_hash, now)).fetchone()
        return dict(row) if row else None


def revoke_remember_token(token_hash):
    with get_connection() as conn:
        conn.execute(
            "DELETE FROM remember_tokens WHERE token_hash = ?",
            (token_hash,)
        )