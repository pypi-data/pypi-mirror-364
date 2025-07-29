import os

from fluidattacks_core.logging.types import JobMetadata


def get_job_metadata() -> JobMetadata:
    """Get the job metadata for applications running in batch environments."""
    return JobMetadata(
        job_id=os.environ.get("AWS_BATCH_JOB_ID"),
        job_queue=os.environ.get("AWS_BATCH_JQ_NAME", "default"),
        compute_environment=os.environ.get("AWS_BATCH_CE_NAME", "default"),
    )
