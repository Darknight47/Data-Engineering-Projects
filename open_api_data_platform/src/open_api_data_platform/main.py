import argparse
from databricks.sdk.runtime import dbutils, spark
from open_api_data_platform.bronze import save_raw_weather
from open_api_data_platform.ingestion import fetch_weather
from open_api_data_platform.logging_config import configure_logging
import logging

logger = logging.getLogger(__name__)


from open_api_data_platform.transformation import (
    transform_weather,
    validate_silver_weather,
    write_silver,
)

def main():
    configure_logging()

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

    try:
        if args.stage == "ingest":
            weather = fetch_weather()

            output_dir = (
                f"/Volumes/{args.catalog}/{args.schema}/bronze_raw"
            )
            file_path = save_raw_weather(weather, output_dir)

            dbutils.jobs.taskValues.set(
                key="bronze_file_path",
                value=str(file_path),
            )

            #print(f"Raw weather data saved to: {file_path}")
            logger.info(
                "Raw weather data saved",
                extra={
                    "event": "bronze_write_succeeded",
                    "stage": "ingest",
                    "file_path": str(file_path),
                },
            )

        elif args.stage == "transform":

            bronze_file_path = dbutils.jobs.taskValues.get(
                taskKey="ingest_weather",
                key="bronze_file_path",
            )

            silver_df = transform_weather(spark, bronze_file_path)

            validate_silver_weather(silver_df=silver_df)

            write_silver(spark=spark, silver_df=silver_df, catalog=args.catalog, schema=args.schema)

            # print(
            #     f"Silver table updated: "
            #     f"{args.catalog}.{args.schema}.weather_observations"
            # )
            logger.info(
                "Silver table updated",
                extra={
                    "event": "silver_write_succeeded",
                    "stage": "transform",
                    "catalog": args.catalog,
                    "schema": args.schema,
                    "table_name": (
                        f"{args.catalog}.{args.schema}."
                        "weather_observations"
                    ),
                },
            )
    except Exception:
        logger.exception(
            "Pipeline stage failed",
            extra={
                "event": "pipeline_stage_failed",
                "stage": args.stage,
                "catalog": args.catalog,
                "schema": args.schema,
            },
        )
        raise

if __name__ == "__main__":
    main()