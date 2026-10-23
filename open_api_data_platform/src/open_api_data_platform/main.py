import argparse
from databricks.sdk.runtime import spark
#from open_api_data_platform import taxis

from open_api_data_platform.bronze import save_raw_weather
from open_api_data_platform.ingestion import fetch_weather


def main():
    parser = argparse.ArgumentParser(
        description="Weather ingestion and transformation pipeline."
    )
    parser.add_argument("--catalog", required=True)
    parser.add_argument("--schema", required=True)
    parser.add_argument(
        "--stage",
        choices=["ingest", "transform"],
        required=True,
    )
    args = parser.parse_args()

    if args.stage == "ingest":
        weather = fetch_weather()

        output_dir = (
            f"/Volumes/{args.catalog}/{args.schema}/bronze_raw"
        )
        file_path = save_raw_weather(weather, output_dir)

        # Pass the exact file to the next task in the Databricks Job.
        from databricks.sdk.runtime import dbutils

        dbutils.jobs.taskValues.set(
            key="bronze_file_path",
            value=str(file_path),
        )

        print(f"Raw weather data saved to: {file_path}")

    elif args.stage == "transform":
        from databricks.sdk.runtime import dbutils, spark
        from open_api_data_platform.transformation import (
            transform_weather,
            write_silver,
        )

        bronze_file_path = dbutils.jobs.taskValues.get(
            taskKey="ingest_weather",
            key="bronze_file_path",
        )

        silver_df = transform_weather(spark, bronze_file_path)
        write_silver(spark=spark, silver_df=silver_df, catalog=args.catalog, schema=args.schema)

        print(
            f"Silver table updated: "
            f"{args.catalog}.{args.schema}.weather_observations"
        )



if __name__ == "__main__":
    main()