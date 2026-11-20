from typing import Any, Dict, List, Tuple

from worldbank_etl.logger import get_logger

logger = get_logger(__name__)

REQUIRED_FIELDS = [
    "country_code",
    "country_name",
    "indicator_code",
    "indicator_name",
    "year",
]


def validate_records(
    records: List[Dict[str, Any]]
) -> Tuple[bool, List[str]]:
    """
    Validate transformed World Bank records.

    Returns:
        (is_valid, errors)
    """
    errors = []
    seen_keys = set()

    for index, record in enumerate(records):
        for field in REQUIRED_FIELDS:
            if record.get(field) is None:
                errors.append(
                    f"Record {index}: missing required field '{field}'"
                )

        year = record.get("year")
        if year is not None and not 1900 <= year <= 2100:
            errors.append(
                f"Record {index}: invalid year '{year}'"
            )

        value = record.get("value")
        if value is not None and value < 0:
            errors.append(
                f"Record {index}: negative value '{value}'"
            )

        key = (
            record.get("country_code"),
            record.get("indicator_code"),
            record.get("year"),
        )

        if key in seen_keys:
            errors.append(
                f"Record {index}: duplicate record for key {key}"
            )
        else:
            seen_keys.add(key)

    is_valid = len(errors) == 0

    if is_valid:
        logger.info(
            "Validation passed. Records checked: %s",
            len(records)
        )
    else:
        logger.error(
            "Validation failed. Error count: %s",
            len(errors)
        )

    return is_valid, errors