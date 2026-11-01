
import logging
from pyspark.sql import DataFrame
from pyspark.sql import functions as F
from delta.tables import DeltaTable
from pyspark.sql import SparkSession

logger = logging.getLogger(__name__)

# Gold Transformation
def build_daily_summary(silver_df: DataFrame) -> DataFrame: 
    """Aggregate hourly weather forecasts into daily summries."""

    daily_df = (
        silver_df.withColumn(
            "forecast_date",
            F.to_date("forecast_time"),
        )
        .groupBy(
            "forecast_date",
            "latitude",
            "longitude",
            "timezone",
        )
        .agg(
            F.avg("temperature_c").alias("avg_temperature_c"),
            F.min("temperature_c").alias("min_temperature_c"),
            F.max("temperature_c").alias("max_temperature_c"),
            F.avg("humidity_percent").alias("avg_humidity_percent"),
            F.count("*").alias("forecast_hours"),
        )
        .withColumn(
            "processed_at",
            F.current_timestamp(),
        )
    )

    logger.info(
        "Daily weather summary built",
        extra={
            "event": "gold_summary_built",
            "stage": "gold",
        },
    )

    return daily_df


# Gold Validation
def validate_gold(gold_df: DataFrame) -> None:
    """Validate the daily weather summary."""

    required_columns = [
        "forecast_date",
        "latitude",
        "longitude",
        "timezone",
        "avg_temperature_c",
        "min_temperature_c",
        "max_temperature_c",
        "avg_humidity_percent",
        "forecast_hours",
        "processed_at",
    ]

    missing_columns = [
        column
        for column in required_columns
        if column not in gold_df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Gold DataFrame is missing columns: {missing_columns}"
        )

    invalid_condition = (
        F.col("forecast_date").isNull()
        | F.col("latitude").isNull()
        | F.col("longitude").isNull()
        | F.col("timezone").isNull()
        | F.col("avg_temperature_c").isNull()
        | F.col("min_temperature_c").isNull()
        | F.col("max_temperature_c").isNull()
        | F.col("avg_humidity_percent").isNull()
        | F.col("forecast_hours").isNull()
        | F.col("processed_at").isNull()
        | (F.col("avg_temperature_c") < -90)
        | (F.col("avg_temperature_c") > 65)
        | (F.col("min_temperature_c") > F.col("max_temperature_c"))
        | (F.col("avg_humidity_percent") < 0)
        | (F.col("avg_humidity_percent") > 100)
        | (F.col("forecast_hours") <= 0)
    )

    invalid_count = gold_df.filter(invalid_condition).count()

    if invalid_count > 0:
        logger.error(
            "Gold data-quality validation failed",
            extra={
                "event": "gold_validation_failed",
                "stage": "gold",
                "invalid_count": invalid_count,
            },
        )

        raise ValueError(
            f"Gold data-quality validation failed: "
            f"{invalid_count} invalid row(s)"
        )


# Gold write (Persistence)
def write_gold(spark: SparkSession, gold_df: DataFrame, catalog: str, schema: str) -> None:
    """Upsert daily summaries into the Gold Delta table."""

    table_name = f"{catalog}.{schema}.weather_daily_summary"

    if not spark.catalog.tableExists(table_name):
        (
            gold_df.write
            .format("delta")
            .saveAsTable(table_name)
        )

        logger.info(
            "Gold table created",
            extra={
                "event": "gold_table_created",
                "stage": "gold",
                "table_name": table_name,
            },
        )
        return

    target = DeltaTable.forName(spark, table_name)

    (
        target.alias("target")
        .merge( # UPSERT/UPDATE operation
            gold_df.alias("source"),
            """
            target.forecast_date = source.forecast_date
            AND target.latitude = source.latitude
            AND target.longitude = source.longitude
            """,
        )
        .whenMatchedUpdateAll()
        .whenNotMatchedInsertAll()
        .execute()
    )

    logger.info(
        "Gold table upsert completed",
        extra={
            "event": "gold_write_succeeded",
            "stage": "gold",
            "table_name": table_name,
        },
    )
