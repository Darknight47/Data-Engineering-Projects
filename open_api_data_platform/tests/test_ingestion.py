import pytest

from open_api_data_platform.ingestion import validate_weather

@pytest.fixture
def valid_hourly_response():
    return {
        "latitude": 59.3293,
        "longitude": 18.0686,
        "timezone": "Europe/Stockholm",
        "hourly": {
            "time": [
                "2026-10-26T00:00",
                "2026-10-26T01:00",
            ],
            "temperature_2m": [8.2, 7.9],
            "relative_humidity_2m": [85, 87],
        },
    }


def test_validate_weather_accepts_valid_response(valid_hourly_response):
    assert validate_weather(valid_hourly_response) == valid_hourly_response

def test_validate_weather_rejects_missing_hourly():
    with pytest.raises(ValueError, match="hourly"):
        validate_weather({"latitude": 59.3293})

def test_validate_weather_rejects_missing_measurement():
    data = {
        "hourly": {
            "time": ["2026-10-26T00:00"],
            "temperature_2m": [8.2],
        }
    }

    with pytest.raises(ValueError, match="relative_humidity_2m"):
        validate_weather(data)


def test_validate_weather_rejects_non_list_measurement():
    data = {
        "hourly": {
            "time": ["2026-10-26T00:00"],
            "temperature_2m": 8.2,
            "relative_humidity_2m": [85],
        }
    }

    with pytest.raises(ValueError, match="must be a list"):
        validate_weather(data)

def test_validate_weather_rejects_mismatched_array_lengths():
    data = {
        "hourly": {
            "time": ["2026-10-26T00:00", "2026-10-26T01:00"],
            "temperature_2m": [8.2],
            "relative_humidity_2m": [85, 87],
        }
    }

    with pytest.raises(ValueError, match="matching lengths"):
        validate_weather(data)

def test_validate_weather_rejects_empty_hourly_data():
    data = {
        "hourly": {
            "time": [],
            "temperature_2m": [],
            "relative_humidity_2m": [],
        }
    }

    with pytest.raises(ValueError, match="must not be empty"):
        validate_weather(data)
