import argparse
from databricks.sdk.runtime import dbutils, spark
from open_api_data_platform.bronze import save_raw_weather
from open_api_data_platform.ingestion import fetch_weather
from open_api_data_platform.logging_config import configure_logging
import logging

logger = logging.getLogger(__name__)

# Silver layer imports
from open_api_data_platform.transformation import (
    transform_weather,
    validate_silver_weather,
    write_silver
)

# Gold layer imports
from open_api_data_platform.gold import (
    build_daily_summary,
    validate_gold,
    write_gold,
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
        choices=["ingest", "transform", "gold"],
        required=True,
    )
    args = parser.parse_args()

    try:
        # Ingest stage: Fetch weather data and save to Bronze layer
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
        # Silver layer processing
        elif args.stage == "transform":

            bronze_file_path = dbutils.jobs.taskValues.get(
                taskKey="ingest_weather",
                key="bronze_file_path",
            )

            silver_df = transform_weather(spark, bronze_file_path)

            validate_silver_weather(silver_df=silver_df)

            write_silver(spark=spark, silver_df=silver_df, catalog=args.catalog, schema=args.schema)

            logger.info(
                "Silver table updated",
                extra={
                    "event": "silver_write_succeeded",
                    "stage": "transform",
                    "catalog": args.catalog,
                    "schema": args.schema,
                    "table_name": (
                        f"{args.catalog}.{args.schema}."
                        "weather_forecasts"
                    ),
                },
            )

        # Gold layer processing
        elif args.stage == "gold":
            silver_table = f"{args.catalog}.{args.schema}.weather_forecasts"

            logger.info(
                "Starting Gold processing",
                extra={
                    "event": "gold_processing_started",
                    "stage": "gold",
                    "table_name": silver_table
                },
            )

            silver_df = spark.table(silver_table)

            gold_df = build_daily_summary(silver_df)

            validate_gold(gold_df=gold_df)

            write_gold(spark=spark, gold_df=gold_df, catalog=args.catalog, schema=args.schema)

            logger.info(
                "Gold table updated",
                extra={
                    "event": "gold_write_succeeded",
                    "stage": "gold",
                    "catalog": args.catalog,
                    "schema": args.schema,
                    "table_name": (
                        f"{args.catalog}.{args.schema}."
                        "weather_daily_summary"
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