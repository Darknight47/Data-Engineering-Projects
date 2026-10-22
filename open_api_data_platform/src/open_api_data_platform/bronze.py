
import json
from datetime import datetime, timezone
from pathlib import Path


def save_raw_weather(data: dict, output_dir: str) -> Path:
    """Persist a raw weather API response as a timestamped JSON file."""
    volume_path = Path(output_dir)
    volume_path.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now(timezone.utc).strftime(
        "%Y%m%dT%H%M%S%fZ"
    )
    file_path = volume_path / f"weather_{timestamp}.json"

    with file_path.open("w", encoding="utf-8") as file:
        json.dump(data, file, indent=2)

    return file_path
