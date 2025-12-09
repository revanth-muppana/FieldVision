import json
import time
import sys
import os

# Boilerplate to import database.py from parent directory
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
import database
ph = database.get_placeholder()

def analyze_weather(weather_json):
    #Takes raw JSON and returns a Risk Score (0-100) and Label.
    data = json.loads(weather_json)
    
    # Defaults
    wind_speed = 0
    temp = 70
    description = "Unknown"

    # --- PARSING LOGIC (ROBUST) ---
    # We try the Standard Nested format FIRST. 
    # This works for Real API data AND the new Nested Mock data.
    try:
        forecast = data['list'][0] # Get the immediate forecast
        wind_speed = forecast['wind']['speed']
        temp = forecast['main']['temp']
        description = forecast['weather'][0]['description']
    except (KeyError, IndexError, TypeError):
        # Fallback: If that fails, checks if it's the old "Flat" mock data
        if data.get("mock"):
            wind_speed = data.get("wind", 0)
            temp = data.get("temp", 70)
            description = "Mock Data"
        else:
            return 0, "Unknown", "Parse Error"

    # --- BUSINESS LOGIC ---
    risk_score = 0
    reasons = []

    # Rule 1: High Wind is bad for passing/kicking
    if wind_speed > 20:
        risk_score += 80
        reasons.append(f"Extreme Wind ({wind_speed}mph)")
    elif wind_speed > 15:
        risk_score += 40
        reasons.append(f"High Wind ({wind_speed}mph)")

    # Rule 2: Freezing Cold is bad for scoring
    if temp < 10:
        risk_score += 30
        reasons.append(f"Deep Freeze ({temp}F)")
    elif temp < 32:
        risk_score += 10
        reasons.append(f"Freezing ({temp}F)")

    # Normalize Logic
    if risk_score > 100: risk_score = 100
    
    # Generate Label
    if risk_score >= 50:
        label = "HIGH"
    elif risk_score >= 20:
        label = "MEDIUM"
    else:
        label = "LOW"

    details = ", ".join(reasons) if reasons else "Good Conditions"
    
    return risk_score, label, details

def run_analysis():
    print("--- Starting Analysis ---")
    conn = database.get_db_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM game_risk")
    cursor.execute("DELETE FROM sqlite_sequence WHERE name='game_risk'")

    # 1. Fetch the LATEST raw record for every unique stadium
    # (This complex SQL ensures we don't re-analyze old data repeatedly)
    cursor.execute('''
        SELECT stadium, team, forecast_json 
        FROM raw_weather 
        GROUP BY stadium 
        HAVING max(collected_at)
    ''')
    
    raw_records = cursor.fetchall()
    print(f"Found {len(raw_records)} stadiums to analyze.")

    for row in raw_records:
        stadium = row['stadium']
        team = row['team']
        raw_json = row['forecast_json']

        score, label, details = analyze_weather(raw_json)

        print(f"Analyzed {stadium}: Risk={label} ({score}) -> {details}")

        query = f'''
                INSERT INTO game_risk (stadium, team, risk_score, risk_label, details, analyzed_at)
                VALUES ({ph}, {ph}, {ph}, {ph}, {ph}, {ph})
            '''
        values = (stadium, team, score, label, details, time.time())
            
        cursor.execute(query, values)
    
    conn.commit()
    conn.close()
    print("--- Analysis Complete ---")

if __name__ == "__main__":
    run_analysis()