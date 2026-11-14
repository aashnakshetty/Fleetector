import os
import requests
import pandas as pd
from datetime import datetime, timezone
from dotenv import load_dotenv
from sqlalchemy import create_engine

# Load the secret DATABASE_URL from your .env file
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

HUBS = [
    {"city": "Mumbai", "lat": 19.0760, "lon": 72.8777},
    {"city": "Delhi NCR", "lat": 28.6139, "lon": 77.2090},
    {"city": "Bengaluru", "lat": 12.9716, "lon": 77.5946},
    {"city": "Hyderabad", "lat": 17.3850, "lon": 78.4867},
    {"city": "Pune", "lat": 18.5204, "lon": 73.8567},
    {"city": "Chennai", "lat": 13.0827, "lon": 80.2707},
]

def calculate_risk(rain_mm, wind_kmh, pm25):
    """Scores delivery disruption risk for 10-min quick-commerce fleets."""
    if rain_mm >= 5.0 or wind_kmh >= 35.0 or pm25 >= 150.0:
        return "High Surge Risk"
    elif rain_mm >= 1.0 or wind_kmh >= 20.0 or pm25 >= 90.0:
        return "Moderate Delay Risk"
    return "Normal"

def run_pipeline():
    records = []
    run_time = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

    for hub in HUBS:
        w_url = f"https://api.open-meteo.com/v1/forecast?latitude={hub['lat']}&longitude={hub['lon']}&current=temperature_2m,rain,wind_gusts_10m"
        weather = requests.get(w_url, timeout=10).json().get("current", {})

        aq_url = f"https://air-quality-api.open-meteo.com/v1/air-quality?latitude={hub['lat']}&longitude={hub['lon']}&current=pm2_5"
        aq = requests.get(aq_url, timeout=10).json().get("current", {})

        temp = weather.get("temperature_2m", 0.0)
        rain = weather.get("rain", 0.0)
        wind = weather.get("wind_gusts_10m", 0.0)
        pm25 = aq.get("pm2_5", 0.0)

        records.append({
            "recorded_at_utc": run_time,
            "city": hub["city"],
            "temp_c": temp,
            "rain_mm": rain,
            "wind_gusts_kmh": wind,
            "pm2_5": pm25,
            "disruption_risk": calculate_risk(rain, wind, pm25)
        })

    df = pd.DataFrame(records)
    print("\n--- LIVE FLEETECTOR DATA ---")
    print(df.to_string(index=False))

    # Connect to Neon PostgreSQL and save the rows!
    engine = create_engine(DATABASE_URL, pool_pre_ping=True)
    df.to_sql("delivery_disruptions", engine, if_exists="append", index=False)
    print("\n✅ Success! 6 live rows saved to Neon PostgreSQL database!")

if __name__ == "__main__":
    run_pipeline()