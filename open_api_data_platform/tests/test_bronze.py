
import json

from open_api_data_platform.bronze import save_raw_weather


def test_save_raw_weather_creates_json_file(tmp_path):
    data = {
        "current": {
            "time": "2026-10-22T12:00",
            "temperature_2m": 12.5,
            "relative_humidity_2m": 72,
        }
    }

    file_path = save_raw_weather(data, str(tmp_path))

    assert file_path.exists()
    assert file_path.name.startswith("weather_")
    assert file_path.suffix == ".json"

    saved_data = json.loads(file_path.read_text(encoding="utf-8"))
    assert saved_data == data
