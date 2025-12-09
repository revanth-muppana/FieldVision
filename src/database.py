import os
import urllib.parse

# Determine if we are on Heroku (Postgres) or Local (SQLite)
# Heroku automatically sets 'DATABASE_URL'
DATABASE_URL = os.environ.get('DATABASE_URL')

def get_db_connection():
    if DATABASE_URL:
        # --- HEROKU (Postgres) ---
        import psycopg2
        import psycopg2.extras
        
        conn = psycopg2.connect(DATABASE_URL, sslmode='require', cursor_factory=psycopg2.extras.RealDictCursor)
        return conn
    else:
        # --- LOCAL (SQLite) ---
        import sqlite3
        
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        DB_PATH = os.path.join(BASE_DIR, 'weather_data.db')
        
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        return conn

def init_db():
    """Creates tables. Handles syntax differences between SQLite and Postgres."""
    conn = get_db_connection()
    c = conn.cursor()
    
    # Postgres uses SERIAL for auto-increment, SQLite uses INTEGER PRIMARY KEY
    # We use a trick: standard SQL usually works for simple creates, 
    # but let's be safe with basic TEXT/INT types.
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS raw_weather (
            id SERIAL PRIMARY KEY,  -- 'SERIAL' works in Postgres, might fail in SQLite
            stadium TEXT NOT NULL,
            team TEXT NOT NULL,
            collected_at REAL NOT NULL,
            forecast_json TEXT NOT NULL
        )
    '''.replace("SERIAL PRIMARY KEY", "INTEGER PRIMARY KEY AUTOINCREMENT") if not DATABASE_URL else '''
        CREATE TABLE IF NOT EXISTS raw_weather (
            id SERIAL PRIMARY KEY,
            stadium TEXT NOT NULL,
            team TEXT NOT NULL,
            collected_at REAL NOT NULL,
            forecast_json TEXT NOT NULL
        )
    ''')
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS game_risk (
            id SERIAL PRIMARY KEY,
            stadium TEXT NOT NULL,
            team TEXT NOT NULL,
            risk_score INTEGER NOT NULL,
            risk_label TEXT NOT NULL,
            details TEXT,
            analyzed_at REAL NOT NULL
        )
    '''.replace("SERIAL PRIMARY KEY", "INTEGER PRIMARY KEY AUTOINCREMENT") if not DATABASE_URL else '''
        CREATE TABLE IF NOT EXISTS game_risk (
            id SERIAL PRIMARY KEY,
            stadium TEXT NOT NULL,
            team TEXT NOT NULL,
            risk_score INTEGER NOT NULL,
            risk_label TEXT NOT NULL,
            details TEXT,
            analyzed_at REAL NOT NULL
        )
    ''')
    
    conn.commit()
    conn.close()
    print("Database initialized.")

def get_placeholder():
    """Returns '?' for SQLite and '%s' for Postgres"""
    return '%s' if DATABASE_URL else '?'

# Run init immediately on import to ensure tables exist
init_db()