import pytest

from open_api_data_platform.ingestion import validate_weather


def test_validate_weather_accepts_valid_response():
    data = {
        "current": {
            "time": "2026-10-22T12:00",
            "temperature_2m": 12.5,
            "relative_humidity_2m": 72,
        }
    }

    assert validate_weather(data) == data


def test_validate_weather_rejects_missing_current():
    with pytest.raises(ValueError, match="current"):
        validate_weather({"latitude": 59.3293})


def test_validate_weather_rejects_missing_measurement():
    data = {
        "current": {
            "time": "2026-10-22T12:00",
            "temperature_2m": 12.5,
        }
    }

    with pytest.raises(ValueError, match="relative_humidity_2m"):
        validate_weather(data)
