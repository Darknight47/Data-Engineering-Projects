import json
import urllib.parse
import urllib.request

API_URL = "https://api.open-meteo.com/v1/forecast"


def fetch_current_weather(latitude: float, longitude: float) -> dict:
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "current": (
            "temperature_2m,"
            "relative_humidity_2m,"
            "precipitation,"
            "rain,"
            "snowfall,"
            "weather_code,"
            "wind_speed_10m,"
            "wind_direction_10m,"
            "is_day"
        ),
        "timezone": "UTC",
    }

    url = f"{API_URL}?{urllib.parse.urlencode(params)}"

    request = urllib.request.Request(
        url,
        headers={"Accept": "application/json"},
    )

    with urllib.request.urlopen(request, timeout=30) as response:
        return json.loads(response.read().decode("utf-8"))