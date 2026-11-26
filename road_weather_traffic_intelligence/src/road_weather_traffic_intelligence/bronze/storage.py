
import json
from datetime import datetime, timezone
from pathlib import Path


def save_raw_response(response: dict, source: str, data_type: str, metadata: dict, base_path: str) -> Path:
    ingested_at = datetime.now(timezone.utc)

    record = {
        "source": source,
        "data_type": data_type,
        "ingested_at": ingested_at.isoformat(),
        **metadata,
        "data": response,
    }

    output_dir = Path(base_path)
    output_dir.mkdir(parents=True, exist_ok=True)

    filename = ingested_at.strftime("%Y-%m-%dT%H-%M-%S-%f") + ".json"
    output_path = output_dir / filename

    with output_path.open("w", encoding="utf-8") as file:
        json.dump(record, file, indent=2)

    return output_path
