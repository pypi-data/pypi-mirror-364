import logging
import logging.config
from venv import logger

logging.config.dictConfig(
    {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "simple": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "simple",
                "level": logging.DEBUG,
            },
        },
        "loggers": {
            "anomalytda_client": {"handlers": ["console"], "level": logging.DEBUG, "propagate": False},
        },
    }
)

logger = logging.getLogger("anomalytda_client")
logger.setLevel(logging.DEBUG)
