from unittest.mock import patch

import pytest

from worldbank_etl.pipeline import run_pipeline


from worldbank_etl.config import load_settings


@pytest.fixture
def mock_settings():
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
        "LOG_LEVEL": "INFO",
        "DB_HOST": "localhost",
        "DB_PORT": "5432",
        "DB_NAME": "worldbank_etl",
        "DB_USER": "postgres",
        "DB_PASSWORD": "postgres",
        "DB_SCHEMA": "public",
        "DB_TABLE": "world_bank_observations",
        "DB_BATCH_SIZE": "1000",
    })


@patch("worldbank_etl.pipeline.load_records")
@patch("worldbank_etl.pipeline.validate_records")
@patch("worldbank_etl.pipeline.transform_records")
@patch("worldbank_etl.pipeline.extract_all_pages")
@patch("worldbank_etl.pipeline.configure_logging")
@patch("worldbank_etl.pipeline.load_settings")
def test_pipeline_success(
    mock_load_settings,
    mock_configure_logging,
    mock_extract,
    mock_transform,
    mock_validate,
    mock_load,
    mock_settings,
):
    settings = mock_settings
    mock_load_settings.return_value = settings

    raw_records = [{"raw": "record"}]
    transformed_records = [{"year": 2024, "value": 100}]

    mock_extract.return_value = (
        {"pages": "1"},
        raw_records,
    )
    mock_transform.return_value = transformed_records
    mock_validate.return_value = (True, [])
    mock_load.return_value = 1

    result = run_pipeline()

    assert result == {
        "api_pages": 1,
        "extracted_records": 1,
        "transformed_records": 1,
        "loaded_records": 1,
    }

    mock_extract.assert_called_once_with(settings)
    mock_transform.assert_called_once_with(raw_records)
    mock_validate.assert_called_once_with(transformed_records)
    mock_load.assert_called_once_with(transformed_records, settings)


@patch("worldbank_etl.pipeline.load_records")
@patch("worldbank_etl.pipeline.validate_records")
@patch("worldbank_etl.pipeline.transform_records")
@patch("worldbank_etl.pipeline.extract_all_pages")
@patch("worldbank_etl.pipeline.configure_logging")
@patch("worldbank_etl.pipeline.load_settings")
def test_pipeline_validation_failure_stops_loading(
    mock_load_settings,
    mock_configure_logging,
    mock_extract,
    mock_transform,
    mock_validate,
    mock_load,
    mock_settings,
):
    mock_load_settings.return_value = mock_settings
    mock_extract.return_value = ({"pages": "1"}, [{"raw": "record"}])
    mock_transform.return_value = [{"year": 2024}]
    mock_validate.return_value = (
        False,
        ["Missing country_code"],
    )

    with pytest.raises(ValueError, match="Data validation failed"):
        run_pipeline()

    mock_load.assert_not_called()


@patch("worldbank_etl.pipeline.load_records")
@patch("worldbank_etl.pipeline.transform_records")
@patch("worldbank_etl.pipeline.extract_all_pages")
@patch("worldbank_etl.pipeline.configure_logging")
@patch("worldbank_etl.pipeline.load_settings")
def test_pipeline_extraction_failure_stops_execution(
    mock_load_settings,
    mock_configure_logging,
    mock_extract,
    mock_transform,
    mock_load,
    mock_settings,
):
    mock_load_settings.return_value = mock_settings
    mock_extract.side_effect = RuntimeError("API unavailable")

    with pytest.raises(RuntimeError, match="API unavailable"):
        run_pipeline()

    mock_transform.assert_not_called()
    mock_load.assert_not_called()