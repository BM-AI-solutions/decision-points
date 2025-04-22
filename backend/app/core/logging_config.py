import logging
import sys
from app.config import settings

# Determine log level from settings
log_level_str = settings.LOG_LEVEL.upper()
log_level = getattr(logging, log_level_str, logging.INFO)

# Basic formatter - can be customized further
# For JSON logging, a library like python-json-logger could be used,
# but sticking to standard library for now.
formatter = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    # Example for more structured (but not pure JSON) format:
    # '{"timestamp": "%(asctime)s", "level": "%(levelname)s", "name": "%(name)s", "message": "%(message)s"}'
)

# Console Handler
stream_handler = logging.StreamHandler(sys.stdout)
stream_handler.setFormatter(formatter)
stream_handler.setLevel(log_level)

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "()": "logging.Formatter",
            "fmt": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
        # Add a JSON formatter definition if a library like python-json-logger is added
        # "json": {
        #     "()": "pythonjsonlogger.jsonlogger.JsonFormatter",
        #     "format": "%(asctime)s %(levelname)s %(name)s %(message)s"
        # }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "default",
            "stream": "ext://sys.stdout",
            "level": log_level_str,
        },
        # Example for JSON handler if library is used
        # "json_console": {
        #     "class": "logging.StreamHandler",
        #     "formatter": "json",
        #     "stream": "ext://sys.stdout",
        #     "level": log_level_str,
        # },
    },
    "loggers": {
        "uvicorn": { # Configure uvicorn loggers
            "handlers": ["console"],
            "level": log_level_str,
            "propagate": False,
        },
        "fastapi": { # Configure fastapi loggers
            "handlers": ["console"],
            "level": log_level_str,
            "propagate": False,
        },
        "app": { # Logger for our application
             "handlers": ["console"], # Use "json_console" for JSON output
             "level": log_level_str,
             "propagate": False, # Prevent root logger from handling 'app' logs again
        }
    },
    "root": { # Root logger configuration
        "level": log_level_str,
        "handlers": ["console"], # Use "json_console" for JSON output
    },
}

def setup_logging():
    """Applies the logging configuration."""
    logging.config.dictConfig(LOGGING_CONFIG)
    logger = logging.getLogger(__name__)
    logger.info(f"Logging configured with level: {log_level_str}")

# Example usage within this module (optional)
# if __name__ == "__main__":
#     setup_logging()
#     root_logger = logging.getLogger()
#     app_logger = logging.getLogger("app")
#     root_logger.debug("This is a root debug message.") # Might not show depending on level
#     root_logger.info("This is a root info message.")
#     app_logger.warning("This is an app warning message.")
#     app_logger.error("This is an app error message.")