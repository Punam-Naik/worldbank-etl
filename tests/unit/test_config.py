
import pytest

from worldbank_etl.config import load_settings


@pytest.fixture
def valid_config():
    return {
        "WB_BASE_URL": "https://api.worldbank.org/v2",
        "WB_COUNTRY": "IND",
        "WB_INDICATOR": "SP.POP.TOTL",
        "WB_START_YEAR": "2000",
        "WB_END_YEAR": "2024",
        "WB_PAGE_SIZE": "100",
        "WB_TIMEOUT_SECONDS": "30",
        "WB_MAX_RETRIES": "3",
        "WB_BACKOFF_FACTOR": "1",
        "APP_ENV": "development",
        "LOG_LEVEL": "INFO"
    }


def test_load_valid_configuration(valid_config):
    settings = load_settings(valid_config)

    assert settings.wb_country == "IND"
    assert settings.wb_indicator == "SP.POP.TOTL"
    assert settings.wb_start_year == 2000
    assert settings.wb_end_year == 2024
    assert settings.wb_page_size == 100


def test_base_url_trailing_slash_removed(valid_config):
    valid_config["WB_BASE_URL"] += "/"

    settings = load_settings(valid_config)

    assert settings.wb_base_url == (
        "https://api.worldbank.org/v2"
    )


def test_invalid_year_range(valid_config):
    valid_config["WB_START_YEAR"] = "2025"
    valid_config["WB_END_YEAR"] = "2000"

    with pytest.raises(ValueError, match="START_YEAR"):
        load_settings(valid_config)


def test_invalid_page_size(valid_config):
    valid_config["WB_PAGE_SIZE"] = "-10"

    with pytest.raises(ValueError, match="PAGE_SIZE"):
        load_settings(valid_config)


def test_missing_required_configuration():
    with pytest.raises(ValueError, match="WB_BASE_URL"):
        load_settings({})
