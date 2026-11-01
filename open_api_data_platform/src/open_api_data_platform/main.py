import argparse
from databricks.sdk.runtime import dbutils, spark
from open_api_data_platform.logging_config import configure_logging
import logging

logger = logging.getLogger(__name__)

from open_api_data_platform.src.open_api_data_platform.pipeline import run_ingestion, run_silver, run_gold  

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
           run_ingestion(catalog=args.catalog, schema=args.schema, dbutils=dbutils)
        # Silver layer processing
        elif args.stage == "transform":
            run_silver(catalog=args.catalog, schema=args.schema, spark=spark)
        # Gold layer processing
        elif args.stage == "gold":
            run_gold(catalog=args.catalog, schema=args.schema, spark=spark)
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