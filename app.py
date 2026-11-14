import os
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy import create_engine, text

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL, pool_pre_ping=True)

app = FastAPI(title="Fleetector Live Monitor")
app.mount("/static", StaticFiles(directory="frontend"), name="static")

@app.get("/")
def serve_dashboard():
    return FileResponse("frontend/index.html")

@app.get("/api/disruptions")
def get_disruptions():
    with engine.connect() as conn:
        latest_query = text("""
            SELECT DISTINCT ON (city)
                city, temp_c, rain_mm, wind_gusts_kmh, pm2_5, disruption_risk, recorded_at_utc
            FROM delivery_disruptions
            ORDER BY city, recorded_at_utc DESC;
        """)
        latest_rows = [dict(row._mapping) for row in conn.execute(latest_query)]

        summary_query = text("SELECT * FROM v_city_disruption_summary;")
        summary_rows = [dict(row._mapping) for row in conn.execute(summary_query)]

    return {"latest": latest_rows, "summary": summary_rows}