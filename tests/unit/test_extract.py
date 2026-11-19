
from unittest.mock import MagicMock, patch

import pytest
import requests

from worldbank_etl.config import load_settings
from worldbank_etl.extract import (
    build_url,
    fetch_page,
    extract_all_pages,
)


@pytest.fixture
def settings():
    """Provide test configuration without reading .env."""

    return load_settings({
        "WB_BASE_URL": "https://api.worldbank.org/v2",
        "WB_COUNTRY": "IND",
        "WB_INDICATOR": "SP.POP.TOTL",
        "WB_START_YEAR": "2000",
        "WB_END_YEAR": "2024",
        "WB_PAGE_SIZE": "100",
        "WB_TIMEOUT_SECONDS": "30",
        "WB_MAX_RETRIES": "3",
        "WB_BACKOFF_FACTOR": "1",
        "APP_ENV": "testing",
        "LOG_LEVEL": "INFO"
    })


@pytest.fixture
def sample_record():
    """Provide a sample World Bank API observation."""

    return {
        "indicator": {
            "id": "SP.POP.TOTL",
            "value": "Population, total"
        },
        "country": {
            "id": "IND",
            "value": "India"
        },
        "countryiso3code": "IND",
        "date": "2024",
        "value": 1450935791,
        "unit": "",
        "obs_status": "",
        "decimal": 0
    }


# --------------------------------------------------
# TEST 1: URL construction
# --------------------------------------------------

def test_build_url(settings):

    url = build_url(settings)

    assert url == (
        "https://api.worldbank.org/v2/"
        "country/IND/indicator/SP.POP.TOTL"
    )


# --------------------------------------------------
# TEST 2: Successful API request
# --------------------------------------------------

def test_fetch_page_success(sample_record):

    session = MagicMock()

    response = MagicMock()
    response.json.return_value = [
        {
            "page": 1,
            "pages": 1,
            "total": 1
        },
        [sample_record]
    ]

    session.get.return_value = response

    metadata, records = fetch_page(
        session=session,
        url="https://api.worldbank.org/v2/test",
        params={"page": 1},
        timeout=30
    )

    assert metadata["page"] == 1
    assert len(records) == 1
    assert records[0]["countryiso3code"] == "IND"

    session.get.assert_called_once()


# --------------------------------------------------
# TEST 3: Invalid API response structure
# --------------------------------------------------

def test_fetch_page_invalid_response():

    session = MagicMock()

    response = MagicMock()
    response.json.return_value = {
        "unexpected": "response"
    }

    session.get.return_value = response

    with pytest.raises(ValueError, match="response structure"):

        fetch_page(
            session=session,
            url="https://api.worldbank.org/v2/test",
            params={"page": 1},
            timeout=30
        )


# --------------------------------------------------
# TEST 4: HTTP failure
# --------------------------------------------------

def test_fetch_page_http_error():

    session = MagicMock()

    response = MagicMock()

    response.raise_for_status.side_effect = requests.HTTPError(
        "500 Internal Server Error"
    )

    session.get.return_value = response

    with pytest.raises(requests.HTTPError):

        fetch_page(
            session=session,
            url="https://api.worldbank.org/v2/test",
            params={"page": 1},
            timeout=30
        )


# --------------------------------------------------
# TEST 5: Pagination
# --------------------------------------------------

def test_extract_all_pages(settings, sample_record):

    session = MagicMock()

    metadata = {
        "page": 1,
        "pages": 3,
        "total": 3
    }

    page_2_record = {**sample_record, "date": "2023"}
    page_3_record = {**sample_record, "date": "2022"}

    with patch(
        "worldbank_etl.extract.fetch_page"
    ) as mock_fetch:

        mock_fetch.side_effect = [
            (metadata, [sample_record]),
            (metadata, [page_2_record]),
            (metadata, [page_3_record])
        ]

        result_metadata, records = extract_all_pages(
            settings=settings,
            session=session
        )

    assert result_metadata["pages"] == 3
    assert len(records) == 3

    assert [record["date"] for record in records] == [
        "2024", "2023", "2022"
    ]

    assert mock_fetch.call_count == 3


# --------------------------------------------------
# TEST 6: Empty API response
# --------------------------------------------------

def test_extract_empty_records(settings):

    session = MagicMock()

    metadata = {
        "page": 1,
        "pages": 1,
        "total": 0
    }

    with patch(
        "worldbank_etl.extract.fetch_page",
        return_value=(metadata, [])
    ):

        result_metadata, records = extract_all_pages(
            settings=settings,
            session=session
        )

    assert result_metadata["total"] == 0
    assert records == []


# --------------------------------------------------
# TEST 7: Session cleanup
# --------------------------------------------------

def test_extract_closes_owned_session(settings, sample_record):

    session = MagicMock()

    metadata = {
        "page": 1,
        "pages": 1,
        "total": 1
    }

    with patch(
        "worldbank_etl.extract.create_http_session",
        return_value=session
    ), patch(
        "worldbank_etl.extract.fetch_page",
        return_value=(metadata, [sample_record])
    ):

        extract_all_pages(settings=settings)

    session.close.assert_called_once()
