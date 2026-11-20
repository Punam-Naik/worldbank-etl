from typing import Any, Dict, List

from worldbank_etl.logger import get_logger

logger = get_logger(__name__)


def transform_records(
    records: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """
    Flatten World Bank API records into a consistent structure.

    Source grain:
        Country + Indicator + Year

    Target fields:
        country_code
        country_name
        indicator_code
        indicator_name
        year
        value
    """
    transformed = []

    for record in records:
        country = record.get("country") or {}
        indicator = record.get("indicator") or {}

        year = record.get("date")
        value = record.get("value")

        if year is None:
            raise ValueError("Record is missing year")

        transformed_record = {
            "country_code": record.get("countryiso3code"),
            "country_name": country.get("value"),
            "indicator_code": indicator.get("id"),
            "indicator_name": indicator.get("value"),
            "year": int(year),
            "value": float(value) if value is not None else None,
        }

        transformed.append(transformed_record)

    logger.info(
        "Transformation completed. Records processed: %s",
        len(transformed)
    )

    return transformed