
import pytest
import json
from pyspark.sql import SparkSession
from datetime import datetime
from pyspark.sql import functions as F
import logging

from open_api_data_platform.transformation import (
    transform_weather,
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
                "2026-10-26T12:00",
                12.5,
                65.0,
                "2026-10-26 12:00:00",
            )
        ],
        [
            "latitude",
            "longitude",
            "timezone",
            "forecast_time",
            "temperature_c",
            "humidity_percent",
            "processed_at",
        ],
    )


def test_valid_weather_passes_validation(valid_weather_df):
    validate_silver_weather(valid_weather_df)


def test_invalid_humidity_fails_validation(valid_weather_df):
    invalid_df = valid_weather_df.withColumn(
        "humidity_percent",
        F.lit(105),
    )

    with pytest.raises(ValueError, match="invalid row"):
        validate_silver_weather(invalid_df)


def test_invalid_temperature_fails_validation(valid_weather_df):

    invalid_df = valid_weather_df.withColumn(
        "temperature_c",
        F.lit(80.0),
    )

    with pytest.raises(ValueError, match="invalid row"):
        validate_silver_weather(invalid_df)

def test_invalid_weather_logs_data_quality_failure(valid_weather_df, caplog):
    
    invalid_df = valid_weather_df.withColumn("humidity_percent", F.lit(105))

    with caplog.at_level(logging.ERROR, 
                         logger="open_api_data_platform_transformation"):
        with pytest.raises(ValueError, match="1 invalid row"):
            validate_silver_weather(invalid_df)

    assert any(
        getattr(record, "event", None) == "data_quality_failed"
        and getattr(record, "invalid_count", None) == 1
        for record in caplog.records
    )
