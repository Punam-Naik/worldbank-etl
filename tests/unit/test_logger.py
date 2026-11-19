
import logging
import pytest

from worldbank_etl.logger import configure_logging, get_logger


def test_get_logger():
    logger = get_logger("worldbank_etl.extract")

    assert isinstance(logger, logging.Logger)
    assert logger.name == "worldbank_etl.extract"


def test_configure_logging():
    configure_logging("DEBUG")

    logger = get_logger("worldbank_etl.extract")

    assert logger.isEnabledFor(logging.DEBUG)


def test_invalid_logging_level():
    with pytest.raises(ValueError, match="Invalid logging level"):
        configure_logging("INVALID")
