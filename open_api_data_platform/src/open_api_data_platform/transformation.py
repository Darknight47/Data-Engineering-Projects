
from delta.tables import DeltaTable
from pyspark.sql import DataFrame
from pyspark.sql import SparkSession
from pyspark.sql.functions import current_timestamp


def transform_weather(
    spark: SparkSession,
    bronze_file_path: str,
) -> DataFrame:
    """Read one raw weather JSON file and prepare a Silver DataFrame."""
    raw_df = (
        spark.read
        .option("multiline", "true")
        .json(bronze_file_path)
    )

    silver_df = raw_df.select(
        "latitude",
        "longitude",
        "timezone",
        "current.time",
        "current.temperature_2m",
        "current.relative_humidity_2m",
    ).selectExpr(
        "latitude",
        "longitude",
        "timezone",
        "`time` AS observation_time",
        "`temperature_2m` AS temperature_c",
        "`relative_humidity_2m` AS humidity_percent",
    )

    return silver_df.withColumn(
        "processed_at",
        current_timestamp(),
    )


def write_silver(
    spark: SparkSession,
    silver_df: DataFrame,
    catalog: str,
    schema: str,
) -> None:
    """Upsert weather observations into the Silver Delta table."""
    table_name = f"{catalog}.{schema}.weather_observations"

    if not spark.catalog.tableExists(table_name):
        # First run: create the table.
        (
            silver_df.write
            .format("delta")
            .saveAsTable(table_name)
        )
        return

    # Subsequent runs: match observations by their business key.
    target = DeltaTable.forName(spark, table_name)

    (
        target.alias("target")
        .merge(
            silver_df.alias("source"),
            """
            target.observation_time = source.observation_time
            AND target.latitude = source.latitude
            AND target.longitude = source.longitude
            """,
        )
        .whenMatchedUpdateAll(
            condition="""
                NOT (
                    target.timezone <=> source.timezone
                    AND target.temperature_c <=> source.temperature_c
                    AND target.humidity_percent <=> source.humidity_percent
                )
            """
        )
        .whenNotMatchedInsertAll()
        .execute()
    )