
import pytest
from pyspark.sql import SparkSession
from datetime import datetime

from open_api_data_platform.transformation import (
    validate_silver_weather,
)


@pytest.fixture
def valid_weather_df(spark: SparkSession):
    return spark.createDataFrame(
        [
            (
                59.3293,
                18.0686,
                "Europe/Stockholm",
                "2026-10-24T12:00",
                12.5,
                65,
                "2026-10-24 12:00:00",
            )
        ],
        [
            "latitude",
            "longitude",
            "timezone",
            "observation_time",
            "temperature_c",
            "humidity_percent",
            "processed_at",
        ],
    )


def test_valid_weather_passes_validation(valid_weather_df):
    validate_silver_weather(valid_weather_df)


def test_invalid_humidity_fails_validation(
    spark: SparkSession,
    valid_weather_df,
):
    invalid_df = valid_weather_df.withColumn(
        "humidity_percent",
        __import__("pyspark.sql.functions", fromlist=["lit"]).lit(105),
    )

    with pytest.raises(ValueError, match="invalid row"):
        validate_silver_weather(invalid_df)


def test_invalid_temperature_fails_validation(
    spark: SparkSession,
    valid_weather_df,
):
    from pyspark.sql import functions as F

    invalid_df = valid_weather_df.withColumn(
        "temperature_c",
        F.lit(80.0),
    )

    with pytest.raises(ValueError, match="invalid row"):
        validate_silver_weather(invalid_df)
