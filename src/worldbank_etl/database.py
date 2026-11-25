from contextlib import contextmanager
from typing import Iterator

import psycopg2
from psycopg2.extensions import connection

from worldbank_etl.config import Settings, load_settings
from worldbank_etl.logger import get_logger

logger = get_logger(__name__)


@contextmanager
def get_db_connection(
    settings: Settings = None,
) -> Iterator[connection]:
    """
    Create and manage a PostgreSQL connection.

    The connection is closed automatically after use.
    """
    if settings is None:
        settings = load_settings()

    conn = None

    try:
        conn = psycopg2.connect(
            host=settings.db_host,
            port=settings.db_port,
            dbname=settings.db_name,
            user=settings.db_user,
            password=settings.db_password,
        )

        logger.info("PostgreSQL connection established")

        yield conn

        conn.commit()
        logger.info("PostgreSQL transaction committed")

    except Exception:
        if conn is not None:
            conn.rollback()

        logger.exception("Database operation failed")
        raise

    finally:
        if conn is not None:
            conn.close()
            logger.info("PostgreSQL connection closed")
