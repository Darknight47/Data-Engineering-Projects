
import logging

from pyspark.sql import SparkSession

from open_api_data_platform.bronze import save_raw_weather
from open_api_data_platform.ingestion import fetch_weather
from open_api_data_platform.silver import (
    transform_weather,
    validate_silver_weather,
    write_silver,
)
from open_api_data_platform.gold import (
    build_daily_summary,
    validate_gold,
    write_gold,
)

logger = logging.getLogger(__name__)


def run_ingestion(catalog: str, schema: str, dbutils):
    """Fetch weather data and persist it in Bronze."""

    weather = fetch_weather()

    output_dir = f"/Volumes/{catalog}/{schema}/bronze_raw"
    file_path = save_raw_weather(weather, output_dir)

    dbutils.jobs.taskValues.set(
        key="bronze_file_path",
        value=str(file_path),
    )

    logger.info(
        "Raw weather data saved",
        extra={
            "event": "bronze_write_succeeded",
            "stage": "ingest",
            "file_path": str(file_path),
        },
    )


def run_silver(spark: SparkSession, catalog: str, schema: str, dbutils):
    """Transform Bronze data and persist it in Silver."""

    bronze_file_path = dbutils.jobs.taskValues.get(
        taskKey="ingest_weather",
        key="bronze_file_path",
    )

    silver_df = transform_weather(spark, bronze_file_path)

    validate_silver_weather(silver_df)

    write_silver(
        spark=spark,
        silver_df=silver_df,
        catalog=catalog,
        schema=schema,
    )

    logger.info(
        "Silver table updated",
        extra={
            "event": "silver_write_succeeded",
            "stage": "transform",
            "catalog": catalog,
            "schema": schema,
            "table_name": f"{catalog}.{schema}.weather_forecasts",
        },
    )


def run_gold(spark: SparkSession, catalog: str, schema: str):
    """Build and persist daily summaries in Gold."""

    silver_table = f"{catalog}.{schema}.weather_forecasts"

    logger.info(
        "Starting Gold processing",
        extra={
            "event": "gold_processing_started",
            "stage": "gold",
            "table_name": silver_table,
        },
    )

    silver_df = spark.table(silver_table)

    gold_df = build_daily_summary(silver_df)

    validate_gold(gold_df)

    write_gold(
        spark=spark,
        gold_df=gold_df,
        catalog=catalog,
        schema=schema,
    )

    logger.info(
        "Gold table updated",
        extra={
            "event": "gold_write_succeeded",
            "stage": "gold",
            "catalog": catalog,
            "schema": schema,
            "table_name": f"{catalog}.{schema}.weather_daily_summary",
        },
    )
