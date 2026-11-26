import argparse
#from databricks.sdk.runtime import spark
import json
from road_weather_traffic_intelligence.sources.trafikverket.traffic_flow import fetch_traffic_flow
from road_weather_traffic_intelligence.sources.open_meteo.current_weather import fetch_current_weather
from road_weather_traffic_intelligence.bronze.storage import save_raw_response
from databricks.sdk.runtime import dbutils
import os


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("--site-id", required=True, type=int)

    args = parser.parse_args()

    print("Project Started!")
    
    os.environ["TRAFIKVERKET_API_KEY"] = dbutils.secrets.get(
        scope="road-weather-secrets",
        key="trafikverket-api-key"
    )

    traffic_flow_response = fetch_traffic_flow(args.site_id)
    traffic_path = save_raw_response(
        response=traffic_flow_response,
        source="trafikverket",
        data_type="traffic_flow",
        metadata={"site_id": args.site_id},
        base_path=(
            "/Volumes/workspace/road_weather_traffic_intelligence/"
            "bronze_raw/trafikverket/traffic_flow"
        ),
    )
    print(f"Raw response saved to: {traffic_path}")

    weather_response = fetch_current_weather(
        latitude=59.30902,
        longitude=18.12303,
    )
    weather_path = save_raw_response(
        response=weather_response,
        source="open_meteo",
        data_type="current_weather",
        metadata={
            "latitude": 59.30902,
            "longitude": 18.12303,
        },
        base_path=(
            "/Volumes/workspace/road_weather_traffic_intelligence/"
            "bronze_raw/open_meteo/current_weather"
        ),
    )
    print(f"Weather response saved to: {weather_path}")

if __name__ == "__main__":
    main()
