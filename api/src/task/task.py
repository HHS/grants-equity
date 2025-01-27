import abc
import logging
import time
from enum import StrEnum
from typing import Any

import src.adapters.db as db
from src.db.models.task_models import JobLog, JobStatus

logger = logging.getLogger(__name__)


class Task(abc.ABC, metaclass=abc.ABCMeta):
    """
    Abstract base class representing an arbitrary
    task that works with the database.

    This approach handles a few basic patterns including:
    - Simple metric aggregation & logging
    - Timing metrics
    - High-level error handling
    """

    class Metrics(StrEnum):
        # Derived classes will implement their own
        # Metrics class with metrics
        pass

    def __init__(self, db_session: db.Session) -> None:
        self.db_session = db_session
        self.metrics: dict[str, Any] = {}
        self.job: JobLog | None = None

    def run(self) -> None:
        job_succeeded = True

        try:
            # Create initial job record
            self.job = JobLog(job_type=self.cls_name(), job_status=JobStatus.STARTED)
            self.db_session.add(self.job)
            self.db_session.commit()

            # Create initial job record
            self.job = JobLog(job_type=self.cls_name(), job_status=JobStatus.STARTED)
            self.db_session.add(self.job)
            self.db_session.commit()

            # Initialize the metrics
            self.initialize_metrics()

            # Run the actual task
            self.run_task()

            logger.info("Starting %s", self.cls_name())
            start = time.perf_counter()

            # Calculate and set a duration
            end = time.perf_counter()
            duration = round((end - start), 3)
            self.set_metrics({"task_duration_sec": duration})

            logger.info("Completed %s in %s seconds", self.cls_name(), duration, extra=self.metrics)
        except Exception:
            job_succeeded = False
            raise
        finally:
            job_status = JobStatus.COMPLETED if job_succeeded else JobStatus.FAILED
            # If the session is active, we can commit the job update
            if job_succeeded:
                self.update_job(job_status, metrics=self.metrics)
            else:
                # If the session is not active due to an error upstream, we need to begin a new transaction
                with self.db_session.begin():
                    self.update_job(job_status, metrics=self.metrics)

    def initialize_metrics(self) -> None:
        zero_metrics_dict: dict[str, Any] = {metric: 0 for metric in self.Metrics}
        self.set_metrics(zero_metrics_dict)

    def set_metrics(self, metrics: dict[str, Any]) -> None:
        self.metrics.update(**metrics)

    def increment(self, name: str, value: int = 1, prefix: str | None = None) -> None:
        if name not in self.metrics:
            self.metrics[name] = 0

        self.metrics[name] += value

        if prefix is not None:
            # Rather than re-implement the above, just re-use the function without a prefix
            self.increment(f"{prefix}.{name}", value, prefix=None)

    def cls_name(self) -> str:
        return self.__class__.__name__

    def update_job(self, job_status: JobStatus, metrics: dict[str, Any] | None = None) -> None:
        if self.job is None:
            raise ValueError("Job is not initialized")

        self.job.job_status = job_status
        self.job.metrics = self.metrics
        self.db_session.commit()

    @abc.abstractmethod
    def run_task(self) -> None:
        """Override to define the task logic"""
        pass
