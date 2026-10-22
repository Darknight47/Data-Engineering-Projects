import json
from urllib.request import urlopen

API_URL = (
    "https://api.open-meteo.com/v1/forecast"
    "?latitude=59.3293"
    "&longitude=18.0686"
    "&current=temperature_2m,relative_humidity_2m"
)



def validate_weather(data: dict) -> dict:
    """Validate the minimum structure expected from the weather API."""
    if not isinstance(data, dict):
        raise ValueError("Weather API response must be a JSON object")

    if "current" not in data or not isinstance(data["current"], dict):
        raise ValueError("Weather API response is missing a valid 'current' object")

    required_fields = (
        "time",
        "temperature_2m",
        "relative_humidity_2m",
    )

    missing_fields = [
        field for field in required_fields
        if field not in data["current"]
    ]

    if missing_fields:
        raise ValueError(
            f"Weather API response is missing fields: {missing_fields}"
        )

    return data


def fetch_weather() -> dict:
    with urlopen(API_URL, timeout=30) as response:
        data = json.loads(response.read().decode("utf-8"))
        return validate_weather(data)


if __name__ == '__main__':
    weather = fetch_weather()
    print(json.dumps(weather, indent= 2))