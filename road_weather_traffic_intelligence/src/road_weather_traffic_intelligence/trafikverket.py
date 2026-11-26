import json
import os
import urllib.request
import xml.etree.ElementTree as ET

from datetime import datetime, timezone
from pathlib import Path

API_URL = "https://api.trafikinfo.trafikverket.se/v2/data.json"

def fetch_traffic_flow(site_id: int) -> dict:
    api_key = os.getenv("TRAFIKVERKET_API_KEY")

    if(not api_key):
        raise ValueError("TRAFIKVERKET_API_KEY environment variable is missing.")

    root = ET.Element("REQUEST")
    ET.SubElement(root, "LOGIN", authenticationkey=api_key)

    query = ET.SubElement(
        root,
        "QUERY",
        objecttype="TrafficFlow",
        schemaversion="1.4",
        limit="10",
    )

    filter_element = ET.SubElement(query, "FILTER")
    ET.SubElement(
        filter_element,
        "EQ",
        name="SiteId",
        value=str(site_id),
    )

    request_body = ET.tostring(root, encoding="utf-8")

    # Send POST request
    request = urllib.request.Request(
        API_URL,
        data=request_body,
        headers={"Content-Type": "text/xml"},
        method="POST",
    )

    with urllib.request.urlopen(request, timeout=30) as response:
        result = json.loads(response.read().decode("utf-8"))

    # Trafikverket can return API errors inside a successful HTTP response
    if "ERROR" in json.dumps(result).upper():
        raise RuntimeError(f"Trafikverket API returned an error: {result}")

    return result

def save_bronze_response(response: dict, site_id: int) -> Path:
    ingested_at = datetime.now(timezone.utc)

    metadata = {
        "source": "trafikverket",
        "object_type": "TrafficFlow",
        "site_id": site_id,
        "ingested_at": ingested_at.isoformat(),
        "data": response
    }

    #timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H-%M-%S")

    output_dir = Path("data/bronze/trafikverket/traffic_flow")
    output_dir.mkdir(parents=True, exist_ok=True)

    filename = ingested_at.strftime("%Y-%m-%dT%H-%M-%S-%f") + ".json"

    output_path = output_dir / filename

    with output_path.open("w", encoding="utf-8") as file:
        json.dump(metadata, file, indent=2)

    return output_path