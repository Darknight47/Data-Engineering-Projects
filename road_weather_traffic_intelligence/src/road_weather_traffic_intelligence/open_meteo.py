import json
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

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

def save_weather_bronze_response(response:dict, latitude:float, longitude:float) -> Path:
    ingested_at = datetime.now(timezone.utc)

    metadata= {
        "source": "open_meteo",
        "data_type": "current_weather",
        "latitude": latitude,
        "longitude": longitude,
        "ingested_at": ingested_at.isoformat(),
        "data": response
    }

    output_dir = Path("data/bronze/open_meteo/current_weather")
    output_dir.mkdir(parents=True, exist_ok=True)

    filename = ingested_at.strftime("%Y-%m-%dT%H-%M-%S-%f") + ".json"
    output_path = output_dir / filename

    with output_path.open("w", encoding="utf-8") as file:
        json.dump(metadata, file, indent=2)

    return output_path