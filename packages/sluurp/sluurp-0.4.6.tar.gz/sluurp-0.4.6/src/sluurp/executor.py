from asyncio import Future
from concurrent.futures import ThreadPoolExecutor
from typing import Callable
import time
from sluurp.job import SBatchScriptJob, submit_sbatch_job

SUBMISSION_TIMEOUT = 10

_executor = None


class Executor(ThreadPoolExecutor):
    def submit(self, fn: Callable, *args, **kwargs) -> Future:
        future = super().submit(fn, *args, **kwargs)
        return future


def submit(job: SBatchScriptJob, timeout=SUBMISSION_TIMEOUT):
    """
    function to submit a job to slurm using SBATCH

    :param SBatchScriptJob job: job script to submit
    """
    global _executor
    if _executor is None:
        _executor = Executor()

    if not isinstance(job, SBatchScriptJob):
        raise TypeError(
            f"job is expected to be an instance of {SBatchScriptJob}. {type(job)} provided"
        )

    future = _executor.submit(submit_sbatch_job, job)
    wait_time = 0
    while job.job_id is None and wait_time < timeout:
        time.sleep(0.1)
        wait_time += 0.1
    future.job_id = job.job_id
    future.collect_logs = job.collect_logs
    if job.job_id is None and future.exception() is None:
        future.set_exception("Unable to submit job within allocated time")

    return future
