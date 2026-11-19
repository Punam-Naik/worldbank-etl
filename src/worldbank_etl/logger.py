
import logging


def configure_logging(log_level: str = "INFO") -> None:
    """
    Configure application-wide logging.

    Logs are written to stdout so they can be collected
    by Docker and other deployment platforms.
    """

    numeric_level = getattr(logging, log_level.upper(), None)

    if not isinstance(numeric_level, int):
        raise ValueError(
            f"Invalid logging level: {log_level}"
        )

    logging.basicConfig(
        level=numeric_level,
        format=(
            "%(asctime)s | "
            "%(levelname)s | "
            "%(name)s | "
            "%(message)s"
        ),
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[
            logging.StreamHandler()
        ],
        force=True
    )


def get_logger(name: str) -> logging.Logger:
    """
    Return a named logger for an application module.
    """

    return logging.getLogger(name)
