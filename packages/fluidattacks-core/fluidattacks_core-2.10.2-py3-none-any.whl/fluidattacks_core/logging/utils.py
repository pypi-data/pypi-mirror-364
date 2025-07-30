import logging
import os

from fluidattacks_core.logging.types import EnvironmentMetadata, JobMetadata


class BatchOnlyFilter(logging.Filter):
    def filter(self, _record: logging.LogRecord) -> bool:
        return os.environ.get("AWS_BATCH_JOB_ID") is not None


class NoBatchFilter(logging.Filter):
    def filter(self, _record: logging.LogRecord) -> bool:
        return os.environ.get("AWS_BATCH_JOB_ID") is None


def get_job_metadata() -> JobMetadata:
    """Get the job metadata for applications running in batch environments."""
    return JobMetadata(
        job_id=os.environ.get("AWS_BATCH_JOB_ID"),
        job_queue=os.environ.get("AWS_BATCH_JQ_NAME", "default"),
        compute_environment=os.environ.get("AWS_BATCH_CE_NAME", "default"),
    )


def get_environment_metadata() -> EnvironmentMetadata:
    """Get the environment metadata for applications running in batch environments."""
    environment = (
        "production" if os.environ.get("CI_COMMIT_REF_NAME", "trunk") == "trunk" else "development"
    )
    commit_sha = os.environ.get("CI_COMMIT_SHA", "00000000")
    commit_short_sha = commit_sha[:8]

    return EnvironmentMetadata(
        environment=environment,
        version=commit_short_sha,
    )
