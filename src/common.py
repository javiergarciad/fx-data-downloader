import logging
import logging.config
from pathlib import Path
import time


def get_project_root():
    """
    Returns project root folder
    """
    return Path(__file__).parent.parent


class UTCFormatter(logging.Formatter):
    """
    Custom UTCFormatter
    """
    converter = time.gmtime


def logging_setup(default_level=logging.INFO):
    """
    Will setup logging with default_level
    :param default_level:
    :return: None
    """
    default_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "simple": {
                "()": UTCFormatter,
                "format": "%(asctime)s -  %(levelname)s - [%(name)s.%(lineno)s]: %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": default_level,
                "formatter": "simple",
                "stream": "ext://sys.stdout",
            },
        },
        "loggers": {
            "default": {
                "level": default_level,
                "handlers": ["console"],
                "propagate": False,
            }
        },
        "root": {
            "level": default_level,
            "handlers": ["console"],
        },
    }

    try:
        logging.config.dictConfig(default_config)
    except Exception as e:
        print(e)
        print("Logging config failed")
        print("Using default config with logging.INFO")
        logging.basicConfig(level=logging.INFO)
