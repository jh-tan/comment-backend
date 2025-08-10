import logging
import logging.config
import os
from app.config.settings import settings

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "%(asctime)s %(name)s %(process)d %(lineno)d %(levelname)s: %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S"
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "default",
            "level": settings.LOG_LEVEL.upper(),
        },
        "error_file": {
            "class": "logging.handlers.TimedRotatingFileHandler",
            "formatter": "default",
            "level": "ERROR",
            "filename": os.path.join(settings.LOG_DIR, "error.log"),
            "when": "midnight",
            "backupCount": 30,
            "encoding": "utf8",
        },
        "all_file": {
            "class": "logging.handlers.RotatingFileHandler",
            "formatter": "default",
            "level": settings.LOG_LEVEL.upper(),
            "filename": os.path.join(settings.LOG_DIR, "app.log"),
            "maxBytes": 10_000_000,
            "backupCount": 5,
            "encoding": "utf8",
        },
    },
    "loggers": {
        "app": {
            "handlers": ["console", "all_file", "error_file"],
            "level": settings.LOG_LEVEL.upper(),
            "propagate": False,
        },
    },
    "root": {
        "handlers": ["console", "all_file", "error_file"],
        "level": settings.LOG_LEVEL.upper(),
    },
}

def setup_logging():
    os.makedirs(settings.LOG_DIR, exist_ok=True)
    
    logging.config.dictConfig(LOGGING_CONFIG)
