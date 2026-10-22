import argparse
from databricks.sdk.runtime import spark
#from open_api_data_platform import taxis

from open_api_data_platform.bronze import save_raw_weather
from open_api_data_platform.ingestion import fetch_weather


def main():
    parser = argparse.ArgumentParser(
        description="Ingest weather data into the Bronze Volume."
    )
    parser.add_argument("--catalog", required=True)
    parser.add_argument("--schema", required=True)
    args = parser.parse_args()

    output_dir = (
        f"/Volumes/{args.catalog}/{args.schema}/bronze_raw"
    )

    weather = fetch_weather()
    file_path = save_raw_weather(weather, output_dir)

    print(f"Raw weather data saved to: {file_path}")


if __name__ == "__main__":
    main()
