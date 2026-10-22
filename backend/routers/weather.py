"""
routers/weather.py
------------------
Weather-based smart alerts using OpenWeatherMap API.
"""

import os
import httpx
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(tags=["Weather"])

OPENWEATHER_KEY = os.getenv("OPENWEATHER_API_KEY", "")


class WeatherRequest(BaseModel):
    lat: float = 28.6139
    lon: float = 77.2090
    fertilizer_recommended: bool = False


class WeatherAlert(BaseModel):
    alert: bool
    message: str
    temp_c: float
    humidity: float
    description: str
    rain_expected: bool


@router.post("/weather/check", response_model=WeatherAlert)
async def check_weather(req: WeatherRequest):
    if not OPENWEATHER_KEY:
        return WeatherAlert(
            alert=req.fertilizer_recommended,
            message="Delay fertilizer due to expected rain." if req.fertilizer_recommended else "No alerts.",
            temp_c=28.0,
            humidity=65.0,
            description="clear sky",
            rain_expected=req.fertilizer_recommended,
        )

    url = f"https://api.openweathermap.org/data/2.5/weather?lat={req.lat}&lon={req.lon}&appid={OPENWEATHER_KEY}&units=metric"
    async with httpx.AsyncClient() as client:
        resp = await client.get(url, timeout=10)
        data = resp.json()

    temp = data.get("main", {}).get("temp", 28)
    humidity = data.get("main", {}).get("humidity", 65)
    desc = data.get("weather", [{}])[0].get("description", "clear sky")
    rain = "rain" in desc.lower() or data.get("rain", {}).get("1h", 0) > 0

    alert_msg = ""
    if req.fertilizer_recommended and rain:
        alert_msg = "Delay fertilizer application — rain expected in your area."
    elif temp > 40:
        alert_msg = "Very high temperature. Avoid field operations during noon."
    elif humidity > 85:
        alert_msg = "High humidity detected. Watch for fungal diseases."

    return WeatherAlert(
        alert=bool(alert_msg),
        message=alert_msg or "Conditions are favorable for farming.",
        temp_c=temp,
        humidity=humidity,
        description=desc,
        rain_expected=rain,
    )
