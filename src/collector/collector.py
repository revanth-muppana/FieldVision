import requests
import json
import time
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
import database
ph = database.get_placeholder()

# 1. CONSTANTS
API_KEY = "1ec8ef9b0f6e6d5b4e8f949713730600"
WEATHER_URL = "https://api.openweathermap.org/data/2.5/forecast"

# 2. DATA SOURCE: Lat/Lon for every NFL Stadium
STADIUMS = {
    "Lambeau Field": {"lat": 44.5013, "lon": -88.0622, "team": "Packers"},
    "AT&T Stadium": {"lat": 32.7473, "lon": -97.0945, "team": "Cowboys"},
    "Arrowhead Stadium": {"lat": 39.0489, "lon": -94.4839, "team": "Chiefs"},
    "Soldier Field": {"lat": 41.8623, "lon": -87.6167, "team": "Bears"},
    "Highmark Stadium": {"lat": 42.7738, "lon": -78.7870, "team": "Bills"},
    "MetLife Stadium": {"lat": 40.8135, "lon": -74.0744, "team": "Jets/Giants"},
    "Gillette Stadium": {"lat": 42.0909, "lon": -71.2643, "team": "Patriots"},
    "Lincoln Financial Field": {"lat": 39.9008, "lon": -75.1675, "team": "Eagles"},
    "Acrisure Stadium": {"lat": 40.4468, "lon": -80.0158, "team": "Steelers"},
    "Cleveland Browns Stadium": {"lat": 41.5061, "lon": -81.6995, "team": "Browns"},
    "M&T Bank Stadium": {"lat": 39.2780, "lon": -76.6227, "team": "Ravens"},
    "Paycor Stadium": {"lat": 39.0955, "lon": -84.5161, "team": "Bengals"},
    "Hard Rock Stadium": {"lat": 25.9580, "lon": -80.2389, "team": "Dolphins"},
    "Nissan Stadium": {"lat": 36.1665, "lon": -86.7713, "team": "Titans"},
    "Lucas Oil Stadium": {"lat": 39.7601, "lon": -86.1639, "team": "Colts"},
    "NRG Stadium": {"lat": 29.6847, "lon": -95.4107, "team": "Texans"},
    "TIAA Bank Field": {"lat": 30.3240, "lon": -81.6373, "team": "Jaguars"},
    "Empower Field": {"lat": 39.7439, "lon": -105.0201, "team": "Broncos"},
    "Allegiant Stadium": {"lat": 36.0909, "lon": -115.1833, "team": "Raiders"},
    "SoFi Stadium": {"lat": 33.9535, "lon": -118.3390, "team": "Rams/Chargers"},
    "Levi's Stadium": {"lat": 37.4014, "lon": -121.9692, "team": "49ers"},
    "Lumen Field": {"lat": 47.5952, "lon": -122.3316, "team": "Seahawks"},
    "State Farm Stadium": {"lat": 33.5276, "lon": -112.2626, "team": "Cardinals"},
    "Mercedes-Benz Stadium": {"lat": 33.7554, "lon": -84.4010, "team": "Falcons"},
    "Bank of America Stadium": {"lat": 35.2251, "lon": -80.8528, "team": "Panthers"},
    "Caesars Superdome": {"lat": 29.9511, "lon": -90.0812, "team": "Saints"},
    "Raymond James Stadium": {"lat": 27.9759, "lon": -82.5033, "team": "Buccaneers"},
    "Ford Field": {"lat": 42.3400, "lon": -83.0456, "team": "Lions"},
    "U.S. Bank Stadium": {"lat": 44.9735, "lon": -93.2575, "team": "Vikings"},
    "FedExField": {"lat": 38.9076, "lon": -76.8645, "team": "Commanders"}
}

def get_weather(lat, lon):
    """
    Fetches the 5-day forecast for a given location.
    """
    # --- 1. TEST INTERCEPTION ---
    # If the test script set the key to this magic string, skip the network entirely!
    if API_KEY == "TEST_KEY_FORCE_MOCK":
        print(f"   [Test Mode] Returning mock data for {lat}, {lon}")
        return {
            "mock": True,
            "list": [{
                "main": {"temp": 25.5},       # Cold!
                "wind": {"speed": 22.0},      # Windy!
                "weather": [{"description": "Mock Blizzard"}]
            }]
        }

    # --- 2. REAL NETWORK REQUEST ---
    params = {
        'lat': lat,
        'lon': lon,
        'appid': API_KEY,
        'units': 'imperial'
    }
    
    try:
        response = requests.get(WEATHER_URL, params=params)
        
        # Handle invalid keys (like if you haven't pasted yours in yet)
        if response.status_code == 401:
            print(f"Warning: 401 Unauthorized. Using mock data.")
            return {
                "mock": True,
                "list": [{
                    "main": {"temp": 72.0},
                    "wind": {"speed": 5.0},
                    "weather": [{"description": "Mock Data (Invalid Key)"}]
                }]
            }
            
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")
        return None

def collect_and_save():
    print(f"--- Starting Collection for {len(STADIUMS)} Stadiums ---")
    
    # Open Database Connection
    conn = database.get_db_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM raw_weather")

    count = 0
    for stadium_name, data in STADIUMS.items():
        print(f"Fetching {stadium_name}...")
        
        weather_data = get_weather(data['lat'], data['lon'])
        
        if weather_data:
            query = f'''
                INSERT INTO raw_weather (stadium, team, collected_at, forecast_json)
                VALUES ({ph}, {ph}, {ph}, {ph})
            '''
            values = (stadium_name, data['team'], time.time(), json.dumps(weather_data))
            
            cursor.execute(query, values)
            count += 1
            conn.commit()
        
        time.sleep(0.2)

    conn.close()
    print(f"--- Finished. Saved {count} records to database. ---")

if __name__ == "__main__":
    # Ensure DB exists before running
    database.init_db()
    collect_and_save()