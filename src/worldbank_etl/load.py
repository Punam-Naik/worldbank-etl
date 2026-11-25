
from typing import Any, Dict, List

from psycopg2.extras import execute_values

from worldbank_etl.config import Settings, load_settings
from worldbank_etl.database import get_db_connection
from worldbank_etl.logger import get_logger

logger = get_logger(__name__)


def load_records(
    records: List[Dict[str, Any]],
    settings: Settings = None,
) -> int:
    """
    Bulk load transformed records into PostgreSQL.

    Uses UPSERT to insert new records and update existing ones.
    Returns the number of records submitted for loading.
    """
    if settings is None:
        settings = load_settings()

    if not records:
        logger.warning("No records received for loading")
        return 0

    # Table and schema identifiers cannot be passed as SQL values.
    # Use psycopg2 SQL composition to quote them safely.
    from psycopg2 import sql

    table_identifier = sql.SQL(".").join([
        sql.Identifier(settings.db_schema),
        sql.Identifier(settings.db_table),
    ])

    insert_query = sql.SQL("""
        INSERT INTO {} (
            country_code,
            country_name,
            indicator_code,
            indicator_name,
            year,
            value
        )
        VALUES %s
        ON CONFLICT (country_code, indicator_code, year)
        DO UPDATE SET
            country_name = EXCLUDED.country_name,
            indicator_name = EXCLUDED.indicator_name,
            value = EXCLUDED.value,
            updated_at = CURRENT_TIMESTAMP
    """).format(table_identifier)

    values = [
        (
            record["country_code"],
            record["country_name"],
            record["indicator_code"],
            record["indicator_name"],
            record["year"],
            record["value"],
        )
        for record in records
    ]

    with get_db_connection(settings) as conn:
        with conn.cursor() as cursor:
            execute_values(
                cursor,
                insert_query.as_string(conn),
                values,
                page_size=settings.db_batch_size,
            )

    logger.info(
        "Database load completed. Records submitted: %s",
        len(records),
    )

    return len(records)
