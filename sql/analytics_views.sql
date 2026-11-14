CREATE OR REPLACE VIEW v_city_disruption_summary AS
SELECT 
    city,
    COUNT(*) AS total_readings,
    ROUND(AVG(temp_c)::numeric, 1) AS avg_temp_c,
    ROUND(MAX(rain_mm)::numeric, 2) AS max_rain_mm,
    ROUND(AVG(wind_gusts_kmh)::numeric, 1) AS avg_wind_kmh,
    ROUND(AVG(pm2_5)::numeric, 1) AS avg_pm25,
    SUM(CASE WHEN disruption_risk = 'High Surge Risk' THEN 1 ELSE 0 END) AS high_risk_events,
    SUM(CASE WHEN disruption_risk = 'Moderate Delay Risk' THEN 1 ELSE 0 END) AS moderate_risk_events
FROM delivery_disruptions
GROUP BY city
ORDER BY avg_pm25 DESC;