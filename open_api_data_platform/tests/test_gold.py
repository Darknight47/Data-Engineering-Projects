
from datetime import datetime

import pytest
from pyspark.sql import SparkSession

from open_api_data_platform.gold import (
    build_daily_summary,
    validate_gold,
)


@pytest.fixture
def hourly_weather_df(spark: SparkSession):

    rows = [
        (
            59.3293,
            18.0686,
            "Europe/Stockholm",
            datetime(2026, 10, 27, 9, 0),
            10.0,
            75.0,
        ),
        (
            59.3293,
            18.0686,
            "Europe/Stockholm",
            datetime(2026, 10, 27, 10, 0),
            12.0,
            68.0,
        ),
        (
            59.3293,
            18.0686,
            "Europe/Stockholm",
            datetime(2026, 10, 27, 11, 0),
            14.0,
            60.0,
        ),                
    ]

    columns = [
        "latitude",
        "longitude",
        "timezone",
        "forecast_time",
        "temperature_c",
        "humidity_percent",
    ] 

    return spark.createDataFrame(rows, columns)


def test_build_daily_summary_calculates_correct_metrics(hourly_weather_df):

    result = build_daily_summary(hourly_weather_df)
    rows = result.collect()

    assert len(rows) == 1

    daily = rows[0]

    assert daily["forecast_date"].isoformat() == "2026-10-27"
    assert daily["avg_temperature_c"] == pytest.approx(12.0)
    assert daily["min_temperature_c"] == pytest.approx(10.0)
    assert daily["max_temperature_c"] == pytest.approx(14.0)
    assert daily["avg_humidity_percent"] == pytest.approx(
        (75.0 + 68.0 + 60.0) / 3
    )
    assert daily["forecast_hours"] == 3
    assert daily["timezone"] == "Europe/Stockholm"


def test_build_daily_summary_calculates_correct_metrics(
    hourly_weather_df,
):
    result = build_daily_summary(hourly_weather_df)

    rows = result.collect()

    assert len(rows) == 1

    daily = rows[0]

    assert daily["forecast_date"].isoformat() == "2026-10-27"
    assert daily["avg_temperature_c"] == pytest.approx(12.0)
    assert daily["min_temperature_c"] == pytest.approx(10.0)
    assert daily["max_temperature_c"] == pytest.approx(14.0)
    assert daily["avg_humidity_percent"] == pytest.approx(
        (75.0 + 68.0 + 60.0) / 3
    )
    assert daily["forecast_hours"] == 3
    assert daily["timezone"] == "Europe/Stockholm"


def test_validate_gold_accepts_valid_data(
    hourly_weather_df,
):
    gold_df = build_daily_summary(hourly_weather_df)

    validate_gold(gold_df)


def test_validate_gold_rejects_invalid_humidity(
    hourly_weather_df,
):
    gold_df = build_daily_summary(hourly_weather_df)

    invalid_df = gold_df.withColumn(
        "avg_humidity_percent",
        gold_df["avg_humidity_percent"] * 2,
    )

    with pytest.raises(ValueError, match="data-quality validation failed"):
        validate_gold(invalid_df)


def test_validate_gold_rejects_missing_columns(
    hourly_weather_df,
):
    gold_df = build_daily_summary(hourly_weather_df)

    incomplete_df = gold_df.drop("forecast_hours")

    with pytest.raises(ValueError, match="forecast_hours"):
        validate_gold(incomplete_df)
