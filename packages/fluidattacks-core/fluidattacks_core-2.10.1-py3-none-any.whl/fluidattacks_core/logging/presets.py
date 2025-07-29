from fluidattacks_core.logging.utils import get_environment_metadata, get_job_metadata

# Main formats
DATE_FORMAT = "%Y-%m-%dT%H:%M:%S%z"
"""
Default date format for logs.
"""


# Configuration for logging in batch environments
_JOB_METADATA = get_job_metadata()
_ENVIRONMENT_METADATA = get_environment_metadata()

BATCH_LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "basic_log": {
            "class": "logging.Formatter",
            "format": (
                "{asctime} {levelname} [{name}] [{filename}:{lineno}] "
                "[trace_id=None span_id=None "
                f"service.name=batch/{_JOB_METADATA.job_queue} "
                f"service.version={_ENVIRONMENT_METADATA.version} "
                f"deployment.environment={_ENVIRONMENT_METADATA.environment} "
                "trace_sampled=False]"
                " - {message}, extra=None"
            ),
            "datefmt": DATE_FORMAT,
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",
            "formatter": "basic_log",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO",
    },
}
"""
Logging configuration dict for batch environments.
"""
