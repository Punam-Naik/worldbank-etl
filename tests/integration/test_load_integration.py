
import os

import pytest
from psycopg2 import sql

from worldbank_etl.config import load_settings
from worldbank_etl.database import get_db_connection
from worldbank_etl.load import load_records
from dotenv import load_dotenv

@pytest.fixture(scope="session")
def integration_settings():
    """
    Load dedicated integration-test database settings.

    Tests run only when RUN_DB_INTEGRATION_TESTS=1.
    """
    if os.getenv("RUN_DB_INTEGRATION_TESTS") != "1":
        pytest.skip("Database integration tests are disabled")

    load_dotenv()

    settings = load_settings()

    from dataclasses import replace

    settings = replace(
        settings,
        db_host=os.getenv("DB_HOST", settings.db_host),
        db_port=int(os.getenv("DB_PORT", settings.db_port)),
        db_schema="public",
        db_table="world_bank_observations_test",
    )

    table = sql.SQL("{}.{}").format(
        sql.Identifier(settings.db_schema),
        sql.Identifier(settings.db_table),
    )

    create_table = sql.SQL("""
        CREATE TABLE IF NOT EXISTS {} (
            id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
            country_code VARCHAR(3) NOT NULL,
            country_name VARCHAR(100) NOT NULL,
            indicator_code VARCHAR(30) NOT NULL,
            indicator_name TEXT NOT NULL,
            year INTEGER NOT NULL,
            value NUMERIC(30, 6),
            created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
            CONSTRAINT uq_world_bank_observation_test
                UNIQUE (country_code, indicator_code, year)
        )
    """).format(table)

    with get_db_connection(settings) as conn:
        with conn.cursor() as cursor:
            cursor.execute(create_table)

    yield settings

    # Remove the dedicated integration-test table after the test session.
    with get_db_connection(settings) as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                sql.SQL("DROP TABLE IF EXISTS {}").format(table)
            )


@pytest.fixture
def clean_table(integration_settings):
    """Start each test with an empty integration-test table."""
    table = sql.SQL("{}.{}").format(
        sql.Identifier(integration_settings.db_schema),
        sql.Identifier(integration_settings.db_table),
    )

    with get_db_connection(integration_settings) as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                sql.SQL("TRUNCATE TABLE {} RESTART IDENTITY").format(table)
            )

    return integration_settings


def sample_record(value=1450935791.0):
    return {
        "country_code": "IND",
        "country_name": "India",
        "indicator_code": "SP.POP.TOTL",
        "indicator_name": "Population, total",
        "year": 2024,
        "value": value,
    }


def fetch_observations(settings):
    table = sql.SQL("{}.{}").format(
        sql.Identifier(settings.db_schema),
        sql.Identifier(settings.db_table),
    )

    with get_db_connection(settings) as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                sql.SQL("""
                    SELECT country_code, indicator_code, year, value
                    FROM {}
                    ORDER BY year
                """).format(table)
            )
            return cursor.fetchall()


def test_database_connection(clean_table):
    with get_db_connection(clean_table) as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT current_database()")
            result = cursor.fetchone()

    assert result[0] == clean_table.db_name


def test_insert_record(clean_table):
    count = load_records(
        [sample_record()],
        clean_table,
    )

    rows = fetch_observations(clean_table)

    assert count == 1
    assert len(rows) == 1
    assert rows[0][0] == "IND"
    assert rows[0][1] == "SP.POP.TOTL"
    assert rows[0][2] == 2024
    assert float(rows[0][3]) == 1450935791.0


def test_upsert_updates_existing_record(clean_table):
    load_records([sample_record(1450935791.0)], clean_table)
    load_records([sample_record(1450935792.0)], clean_table)

    rows = fetch_observations(clean_table)

    assert len(rows) == 1
    assert float(rows[0][3]) == 1450935792.0


def test_repeated_load_does_not_create_duplicates(clean_table):
    record = sample_record()

    load_records([record], clean_table)
    load_records([record], clean_table)
    load_records([record], clean_table)

    rows = fetch_observations(clean_table)

    assert len(rows) == 1


def test_transaction_rollback(clean_table):
    table = sql.SQL("{}.{}").format(
        sql.Identifier(clean_table.db_schema),
        sql.Identifier(clean_table.db_table),
    )

    with pytest.raises(RuntimeError, match="Simulated failure"):
        with get_db_connection(clean_table) as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    sql.SQL("""
                        INSERT INTO {} (
                            country_code,
                            country_name,
                            indicator_code,
                            indicator_name,
                            year,
                            value
                        )
                        VALUES (%s, %s, %s, %s, %s, %s)
                    """).format(table),
                    (
                        "IND",
                        "India",
                        "SP.POP.TOTL",
                        "Population, total",
                        2024,
                        1450935791.0,
                    ),
                )

                raise RuntimeError("Simulated failure")

    rows = fetch_observations(clean_table)

    assert rows == []
