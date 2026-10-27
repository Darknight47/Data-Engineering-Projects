
import logging
from pyspark.sql import DataFrame
from pyspark.sql import functions as F

logger = logging.getLogger(__name__)

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