import logging
import os
import structlog


def convert_log_level_string_to_int(log_level: str) -> int:
    log_levels = {
        "CRITICAL": logging.CRITICAL,
        "ERROR": logging.ERROR,
        "WARNING": logging.WARNING,
        "INFO": logging.INFO,
        "DEBUG": logging.DEBUG,
        "NOTSET": logging.NOTSET,
    }
    if log_level.upper() not in log_levels:
        logging.warning(f"Invalid LOG_LEVEL '{log_level}', defaulting to DEBUG.")
    return log_levels.get(log_level.upper(), logging.DEBUG)


LOG_LEVEL = convert_log_level_string_to_int(os.getenv("LOG_LEVEL", "DEBUG").strip())

structlog.configure(wrapper_class=structlog.make_filtering_bound_logger(LOG_LEVEL))

log = structlog.get_logger()
