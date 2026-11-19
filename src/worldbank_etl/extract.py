
from typing import Any, Dict, List, Optional, Tuple

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from worldbank_etl.config import Settings, load_settings
from worldbank_etl.logger import get_logger


logger = get_logger(__name__)


def build_url(settings: Settings) -> str:
    """
    Build the World Bank indicator endpoint.
    """

    return (
        f"{settings.wb_base_url}/country/"
        f"{settings.wb_country}/indicator/"
        f"{settings.wb_indicator}"
    )


def create_http_session(settings: Settings) -> requests.Session:
    """
    Create an HTTP session with retry and backoff policies.
    """

    retry_strategy = Retry(
        total=settings.wb_max_retries,
        connect=settings.wb_max_retries,
        read=settings.wb_max_retries,
        status=settings.wb_max_retries,
        backoff_factor=settings.wb_backoff_factor,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods={"GET"},
        respect_retry_after_header=True,
        raise_on_status=False
    )

    adapter = HTTPAdapter(max_retries=retry_strategy)

    session = requests.Session()

    session.mount("https://", adapter)
    session.mount("http://", adapter)

    session.headers.update({
        "Accept": "application/json",
        "User-Agent": "worldbank-etl/1.0"
    })

    return session


def fetch_page(
    session: requests.Session,
    url: str,
    params: Dict[str, Any],
    timeout: int
) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
    """
    Fetch one page and separate API metadata from records.
    """

    logger.info("Fetching API page: %s", params["page"])

    response = session.get(
        url,
        params=params,
        timeout=timeout
    )

    response.raise_for_status()

    payload = response.json()

    if not isinstance(payload, list) or len(payload) != 2:
        raise ValueError("Unexpected World Bank API response structure")

    metadata, records = payload

    if not isinstance(metadata, dict):
        raise ValueError("Invalid API metadata")

    if records is None:
        records = []

    if not isinstance(records, list):
        raise ValueError("Invalid API records structure")

    logger.info(
        "Page %s fetched successfully. Records: %s",
        params["page"],
        len(records)
    )

    return metadata, records


def extract_all_pages(
    settings: Optional[Settings] = None,
    session: Optional[requests.Session] = None
) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
    """
    Extract all available pages from the World Bank API.

    Returns:
        metadata: Metadata from the first API response.
        records: Combined records from all pages.
    """

    if settings is None:
        settings = load_settings()

    url = build_url(settings)

    params = {
        "format": "json",
        "date": (
            f"{settings.wb_start_year}:"
            f"{settings.wb_end_year}"
        ),
        "per_page": settings.wb_page_size,
        "page": 1
    }

    owns_session = session is None

    if owns_session:
        session = create_http_session(settings)

    all_records = []
    first_metadata = {}

    try:
        # First API request
        metadata, records = fetch_page(
            session,
            url,
            params,
            settings.wb_timeout_seconds
        )

        first_metadata = metadata
        all_records.extend(records)

        total_pages = int(metadata["pages"])

        logger.info("Total API pages: %s", total_pages)

        # Fetch remaining pages
        for page_number in range(2, total_pages + 1):

            params["page"] = page_number

            _, page_records = fetch_page(
                session,
                url,
                params,
                settings.wb_timeout_seconds
            )

            all_records.extend(page_records)

        logger.info(
            "Extraction completed. Total records: %s",
            len(all_records)
        )

        return first_metadata, all_records

    except (requests.RequestException, ValueError, KeyError, TypeError):
        logger.exception("API extraction failed")
        raise

    finally:
        if owns_session and session is not None:
            session.close()
