import os
import requests

WEATHER_LAT = float(os.environ.get("WEATHER_LAT", "25.04"))
WEATHER_LON = float(os.environ.get("WEATHER_LON", "121.56"))
TIMEZONE = os.environ.get("TIMEZONE", "Asia/Taipei")

WMO_DESCRIPTIONS = {
    0: "Clear sky", 1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
    45: "Foggy", 48: "Foggy",
    51: "Light drizzle", 53: "Drizzle", 55: "Heavy drizzle",
    61: "Light rain", 63: "Rain", 65: "Heavy rain",
    71: "Light snow", 73: "Snow", 75: "Heavy snow",
    80: "Showers", 81: "Showers", 82: "Heavy showers",
    95: "Thunderstorm", 96: "Thunderstorm", 99: "Thunderstorm",
}


def get_weather() -> str:
    try:
        resp = requests.get(
            "https://api.open-meteo.com/v1/forecast",
            params={
                "latitude": WEATHER_LAT,
                "longitude": WEATHER_LON,
                "current": "temperature_2m,apparent_temperature,weathercode",
                "daily": "temperature_2m_max,temperature_2m_min",
                "timezone": TIMEZONE,
                "forecast_days": 1,
            },
            timeout=10,
        )
        resp.raise_for_status()
        data = resp.json()
        current = data["current"]
        daily = data["daily"]
        desc = WMO_DESCRIPTIONS.get(current["weathercode"], "Unknown")
        temp = current["temperature_2m"]
        feels = current["apparent_temperature"]
        high = daily["temperature_2m_max"][0]
        low = daily["temperature_2m_min"][0]
        return f"{desc}, {temp:.0f}°C (feels {feels:.0f}°C) · High {high:.0f}° / Low {low:.0f}°"
    except Exception:
        return "Weather unavailable"
