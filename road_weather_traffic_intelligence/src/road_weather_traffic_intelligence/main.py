import argparse
#from databricks.sdk.runtime import spark
import json
from road_weather_traffic_intelligence.trafikverket import fetch_traffic_flow, save_bronze_response
from road_weather_traffic_intelligence.open_meteo import fetch_current_weather, save_weather_bronze_response


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("--site-id", required=True, type=int)

    args = parser.parse_args()

    print("Project Started!")
    print(f"Collected TrafficFlow Data For {args.site_id}")

    #response = fetch_traffic_flow(args.site_id)
    #output_path = save_bronze_response(response=response, site_id=args.site_id)
    #print(json.dumps(response, indent=2))
    #print(f"Raw response saved to: {output_path}")

    weather_response = fetch_current_weather(
        latitude=59.30902,
        longitude=18.12303,
    )
    #print(json.dumps(weather_response, indent=2))
    weather_path = save_weather_bronze_response(response=weather_response, latitude=59.30902, longitude=18.12303)
    print(f"Weather response saved to: {weather_path}")

if __name__ == "__main__":
    main()
