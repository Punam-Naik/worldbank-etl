
from typing import Any, Dict

from worldbank_etl.config import load_settings
from worldbank_etl.extract import extract_all_pages
from worldbank_etl.logger import configure_logging, get_logger
from worldbank_etl.transform import transform_records
from worldbank_etl.validate import validate_records
from worldbank_etl.load import load_records

logger = get_logger(__name__)


def run_pipeline() -> Dict[str, Any]:
    """
    Execute the complete World Bank ETL pipeline.
    """
    settings = load_settings()
    configure_logging(settings.log_level)

    logger.info("World Bank ETL pipeline started")

    # 1. Extract
    metadata, raw_records = extract_all_pages(settings)

    # 2. Transform
    transformed_records = transform_records(raw_records)

    # 3. Validate
    is_valid, errors = validate_records(transformed_records)

    if not is_valid:
        raise ValueError(
            f"Data validation failed: {errors}"
        )

    # 4. Load
    loaded_count = load_records(
        transformed_records,
        settings,
    )

    result = {
        "api_pages": int(metadata["pages"]),
        "extracted_records": len(raw_records),
        "transformed_records": len(transformed_records),
        "loaded_records": loaded_count,
    }

    logger.info("ETL pipeline completed successfully")
    logger.info("Pipeline summary: %s", result)

    return result


if __name__ == "__main__":
    run_pipeline()
