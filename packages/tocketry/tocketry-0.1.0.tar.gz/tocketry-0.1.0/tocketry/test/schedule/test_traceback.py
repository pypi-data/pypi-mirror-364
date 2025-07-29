import logging
import pytest

from tocketry.repo import RepoHandler, MemoryRepo

from tocketry.conditions.scheduler import SchedulerStarted
from tocketry.core.time.base import TimeDelta
from tocketry.log.log_record import LogRecord
from tocketry.tasks import FuncTask
from tocketry.conditions import TaskStarted, AlwaysTrue


def run_failing():
    raise RuntimeError("Task failed")


@pytest.mark.parametrize("execution", ["main", "thread", "process"])
def test_task_fail_traceback(tmpdir, execution, session):
    # There is a speciality in tracebacks in multiprocessing
    # See: https://bugs.python.org/issue34334

    # TODO: Delete. This has been handled now in test_core.py
    with tmpdir.as_cwd():
        task_logger = logging.getLogger(session.config.task_logger_basename)
        task_logger.handlers = [RepoHandler(repo=MemoryRepo(model=LogRecord))]
        task = FuncTask(
            run_failing,
            name="task",
            start_cond=AlwaysTrue(),
            execution=execution,
            session=session,
        )

        session.config.shut_cond = (TaskStarted(task="task") >= 3) | ~SchedulerStarted(
            period=TimeDelta("20 seconds")
        )
        session.start()

        failures = list(task.logger.get_records(action="fail"))
        assert 3 == len(failures)

        for record in failures:
            tb = record.exc_text
            assert "Traceback (most recent call last):" in tb
            assert "RuntimeError: Task failed" in tb
