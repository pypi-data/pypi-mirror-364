import asyncio
from dataclasses import dataclass
import inspect
from pickle import PicklingError
import sys
import time
import datetime
import logging
import platform
from types import FunctionType, TracebackType
import warnings
from copy import copy
from abc import abstractmethod
import multiprocessing
import threading
from queue import Empty
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    ClassVar,
    List,
    Dict,
    Type,
    Union,
    Tuple,
    Optional,
)
from typing_extensions import Annotated

try:
    from typing import Literal
except ImportError:  # pragma: no cover
    from typing_extensions import Literal

from dataclasses import dataclass, field

from tocketry._base import RedBase
from tocketry.core.condition import BaseCondition, AlwaysFalse, All
from tocketry.core.time import TimePeriod
from tocketry.core.parameters import Parameters
from tocketry.core.log import TaskAdapter
from tocketry.pybox.time import to_timedelta
from tocketry.core.utils import is_pickleable, filter_keyword_args, is_main_subprocess
from tocketry.exc import (
    SchedulerRestart,
    SchedulerExit,
    TaskInactionException,
    TaskTerminationException,
    TaskLoggingError,
    TaskSetupError,
)
from tocketry.core.hook import _Hooker
from tocketry.log import QueueHandler

if TYPE_CHECKING:
    from tocketry import Session
    from tocketry.core.parameters import BaseArgument

_IS_WINDOWS = platform.system()


def _create_session():
    # To avoid circular imports
    from tocketry import Session

    return Session()


@dataclass
class TaskRun:
    start: float
    task: Union[asyncio.Task, threading.Thread, multiprocessing.Process, None]
    run_id: str = None

    # Thread related
    event_terminate: Optional[threading.Event] = None
    event_running: Optional[threading.Event] = None
    exception: Exception = None

    def is_alive(self) -> bool:
        if self.is_main:
            return True
        if self.is_async:
            return not self.task.done()
        return self.task.is_alive()

    async def terminate(self):
        task = self.task
        if self.is_async:
            task.cancel()
            await task
        elif self.is_process:
            task.terminate()
            # Waiting till the termination is finished.
            # Otherwise may try to terminate it many times as the process is alive for a brief moment
            task.join()
        elif self.is_thread:
            self.event_terminate.set()
        else:
            raise TypeError(f"Cannot terminate task: {task!r}")

    @property
    def is_main(self) -> bool:
        return self.task is None

    @property
    def is_process(self) -> bool:
        return isinstance(self.task, multiprocessing.Process)

    @property
    def is_async(self) -> bool:
        return isinstance(self.task, asyncio.Future)

    @property
    def is_thread(self) -> bool:
        return isinstance(self.task, threading.Thread)


@dataclass(eq=False)
class Task(RedBase):
    """Base class for Tasks.

    A task can be a function, command or other procedure that
    does a specific thing. A task can be parametrized by supplying
    session level parameters or parameters on task basis.


    Parameters
    ----------
    name : str, optional
        Name of the task. Ideally, all tasks
        should have unique name. If None, the
        return value of Task.get_default_name()
        is used instead.
    description : str, optional
        Description of the task. This is purely
        for task documentation purpose.
    start_cond : BaseCondition, optional
        Condition that when True the task
        is to be started, by default AlwaysFalse()
    end_cond : BaseCondition, optional
        Condition that when True the task
        will be terminated. Only works for for
        tasks with execution='process' or 'thread'
        if thread termination is implemented in
        the task, by default AlwaysFalse()
    execution : str, {'main', 'thread', 'process'}, default='process'
        How the task is executed. Allowed values
        'main' (run on main thread & process),
        'thread' (run on another thread) and
        'process' (run on another process).
    parameters : Parameters, optional
        Parameters set specifically to the task,
        by default None
    disabled : bool
        If True, the task is not allowed to be run
        regardless of the start_cond,
        by default False
    force_run : bool
        If True, the task will be run once
        regardless of the start_cond,
        by default True
    on_startup : bool
        Run the task on the startup sequence of
        the Scheduler, by default False
    on_shutdown : bool
        Run the task on the shutdown sequence of
        the Scheduler, by default False
    priority : int, optional
        Priority of the task. Higher priority
        tasks are first inspected whether they
        can be executed. Can be any numeric value.
        Setup tasks are recommended to have priority
        >= 40 if they require loaded tasks,
        >= 50 if they require loaded extensions.
        By default 0
    timeout : str, int, timedelta, optional
        If the task has not run in given timeout
        the task will be terminated. Only applicable
        for tasks with execution='process' or
        with execution='thread'.
    daemon : Bool, optional
        Whether run the task as daemon process
        or not. Only applicable for execution='process',
        by default use Scheduler default
    on_exists : str
        What to do if the name of the task already
        exists in the session, options: 'raise',
        'ignore', 'replace', by default use session
        configuration
    logger : str, logger.Logger, optional
        Logger of the task. Typically not needed
        to be set.
    session : tocketry.session.Session, optional
        Session the task is binded to.


    Attributes
    ----------
    session : tocketry.session.Session
        Session the task is binded to.
    logger : TaskAdapter
        Logger of the task. Access the
        log records using task.logger.get_records()


    Examples
    --------
    Minimum example:

    >>> from tocketry.core import Task
    >>> class MyTask(Task):
    ...     def execute(self):
    ...         ... # What the task does.
    ...         return ...

    """

    permanent: bool = False  # Whether the task is not meant to finish (Ie. RestAPI)
    _actions: ClassVar[Tuple] = (
        "run",
        "fail",
        "success",
        "inaction",
        "terminate",
        None,
        "crash",
    )
    fmt_log_message: str = r"Task '{task}' status: '{action}'"

    daemon: Optional[bool] = None
    batches: List[Parameters] = field(
        default_factory=list
    )  # Run batches (parameters). If not empty, run is triggered regardless of starting condition

    # Instance
    # name: Optional[str] - not defined as dataclass field, set manually in __init__
    description: Optional[str] = None  # Description of the task for documentation
    logger_name: Optional[str] = "tocketry.task"  # Logger name to be used in logging the task records
    execution: Optional[Literal["main", "async", "thread", "process"]] = None
    priority: int = 0
    disabled: bool = False
    _force_run: bool = field(default=False, init=False)
    force_termination: bool = False
    _status: Optional[Literal["run", "fail", "success", "terminate", "inaction", "crash"]] = field(
        default=None, init=False
    )  # Latest status of the task
    timeout: Optional[datetime.timedelta] = None

    parameters: Parameters = field(default_factory=Parameters)

    start_cond: Optional[BaseCondition] = field(
        default_factory=AlwaysFalse
    )  #! TODO: Create get_start_cond so that this could also be as string (lazily parsed)
    end_cond: Optional[BaseCondition] = field(default_factory=AlwaysFalse)

    multilaunch: Optional[bool] = None
    on_startup: bool = False
    on_shutdown: bool = False
    func_run_id: Union[Callable, None] = None

    _last_run: Optional[float] = field(default=None, init=False)
    _last_success: Optional[float] = field(default=None, init=False)
    _last_fail: Optional[float] = field(default=None, init=False)
    _last_terminate: Optional[float] = field(default=None, init=False)
    _last_inaction: Optional[float] = field(default=None, init=False)
    _last_crash: Optional[float] = field(default=None, init=False)

    _run_stack: List[TaskRun] = field(default_factory=list, init=False)
    _lock: Optional[Type] = field(default=None, init=False)
    _main_alive: bool = field(default=False, init=False)

    _mark_running = False

    def __post_init__(self):
        """Handle field validation that was previously done by pydantic field validators"""
        # Validate start_cond
        if isinstance(self.start_cond, str):
            from tocketry.parse.condition import parse_condition

            self.start_cond = parse_condition(self.start_cond, session=self.session)
        elif self.start_cond is None:
            self.start_cond = AlwaysFalse()
        else:
            self.start_cond = copy(self.start_cond)

        # Validate end_cond
        if isinstance(self.end_cond, str):
            from tocketry.parse.condition import parse_condition

            self.end_cond = parse_condition(self.end_cond, session=self.session)
        elif self.end_cond is None:
            self.end_cond = AlwaysFalse()
        else:
            self.end_cond = copy(self.end_cond)

        # Validate logger_name
        if isinstance(self.logger_name, str):
            pass  # Already a string, keep as is
        elif self.logger_name is None:
            self.logger_name = self.session.config.task_logger_basename if self.session else "tocketry.task"
        else:
            # Assume it's a logger object
            self.logger_name = self.logger_name.name
            if self.session:
                basename = self.session.config.task_logger_basename
                if not self.logger_name.startswith(basename):
                    raise ValueError(f"Logger name must start with '{basename}' as session finds loggers with names")

        # Validate timeout
        if self.timeout == "never":
            from tocketry.pybox.time import to_timedelta

            self.timeout = datetime.timedelta.max
        elif isinstance(self.timeout, (float, int)):
            from tocketry.pybox.time import to_timedelta

            self.timeout = to_timedelta(self.timeout, unit="s")
        elif self.timeout is not None and not isinstance(self.timeout, datetime.timedelta):
            from tocketry.pybox.time import to_timedelta

            self.timeout = to_timedelta(self.timeout)

        # Validate execution
        valid_executions = {"main", "async", "thread", "process", None}
        if self.execution not in valid_executions:
            raise ValueError(
                f"Invalid execution '{self.execution}'. Must be one of {sorted([e for e in valid_executions if e is not None])}"
            )

        # Validate parameters
        if not isinstance(self.parameters, Parameters):
            self.parameters = Parameters(self.parameters)

        # Handle force_run deprecation
        if self.force_run:
            warnings.warn(
                "Attribute 'force_run' is deprecated. Please use method set_running() instead",
                DeprecationWarning,
            )
            self.batches.append(Parameters())

    # JSON serialization methods (replacement for pydantic field_serializers)
    def _serialize_for_json(self):
        """Custom serialization for JSON compatibility"""
        return {
            "parameters": self.parameters.to_json() if hasattr(self.parameters, "to_json") else str(self.parameters),
            "start_cond": str(self.start_cond),
            "end_cond": str(self.end_cond),
            "session": id(self.session) if self.session else None,
            # Add other fields as needed
        }

    @property
    def logger(self):
        logger = logging.getLogger(self.logger_name)
        return TaskAdapter(logger, task=self)

    def __setattr__(self, name, value):
        """Override setattr to validate name changes"""
        if (name == "name" and hasattr(self, 'session') and value is not None and 
            self.session is not None and hasattr(self.session, "tasks") and
            hasattr(self.session, "config") and self.session.config.task_pre_exist == "raise"):
            # Only check for conflicts if task_pre_exist is "raise"
            # For "ignore" and "rename", let the session handle it in add_task()
            for task in self.session.tasks:
                if task is not self and hasattr(task, "name") and getattr(task, "name", None) == value:
                    raise ValueError(f"Task name '{value}' already exists.")
        super().__setattr__(name, value)

    @property
    def status(self):
        """Get task status"""
        return self._status

    @status.setter
    def status(self, value):
        """Set task status with validation"""
        if value is not None and value not in self._actions:
            raise ValueError(f"Invalid status '{value}'. Must be one of {self._actions}")
        self._status = value

    @property
    def force_run(self):
        """Get force_run value"""
        return self._force_run

    @force_run.setter
    def force_run(self, value):
        """Set force_run value with deprecation warning"""
        if value and not self._force_run:  # Only warn when setting to True from False
            warnings.warn(
                "Attribute 'force_run' is deprecated. Please use method set_running() instead",
                DeprecationWarning,
                stacklevel=2,
            )
            self.batches.append(Parameters())
        self._force_run = value

    def __init__(self, **kwargs):
        """Initialize Task with validation and setup"""

        # Extract values from kwargs
        session = kwargs.get("session")
        name = kwargs.get("name")
        description = kwargs.get("description")
        logger_name = kwargs.get("logger_name", "tocketry.task")
        execution = kwargs.get("execution")
        priority = kwargs.get("priority", 0)
        disabled = kwargs.get("disabled", False)
        force_run = kwargs.get("force_run", False)
        force_termination = kwargs.get("force_termination", False)
        status = kwargs.get("status")
        timeout = kwargs.get("timeout")
        parameters = kwargs.get("parameters")
        start_cond = kwargs.get("start_cond")
        end_cond = kwargs.get("end_cond")
        multilaunch = kwargs.get("multilaunch")
        on_startup = kwargs.get("on_startup", False)
        on_shutdown = kwargs.get("on_shutdown", False)
        func_run_id = kwargs.get("func_run_id")
        daemon = kwargs.get("daemon")
        batches = kwargs.get("batches")
        permanent = kwargs.get("permanent", False)

        # Handle session creation
        if session is None:
            warnings.warn("Task's session not defined. Creating new.", UserWarning)
            session = _create_session()

        # Handle name generation
        if name is None:
            use_instance_naming = session.config.use_instance_naming if session else False
            if use_instance_naming:
                name = str(id(self))
            else:
                # Remove 'name' from kwargs to avoid conflict in get_default_name
                kwargs_copy = {k: v for k, v in kwargs.items() if k != "name"}
                name = self.get_default_name(name=name, **kwargs_copy)

        # Handle deprecated arguments
        if "permanent_task" in kwargs:
            warnings.warn(
                "Argument 'permanent_task' is deprecated. Please use 'permanent'.",
                DeprecationWarning,
            )
            permanent = kwargs.pop("permanent_task")

        # Set up defaults
        if parameters is None:
            parameters = Parameters()
        if start_cond is None:
            start_cond = AlwaysFalse()
        if end_cond is None:
            end_cond = AlwaysFalse()
        if batches is None:
            batches = []

        # Initialize the dataclass fields
        # Set session as instance attribute (overrides class attribute for this instance)
        self.session = session
        # Note: _name is set later after hooks to avoid premature hasattr(task, "name") = True
        self.description = description
        self.logger_name = logger_name
        self.execution = execution
        self.priority = priority
        self.disabled = disabled
        self._force_run = force_run
        self.force_termination = force_termination
        self._status = status
        self.timeout = timeout
        self.parameters = parameters
        self.start_cond = start_cond
        self.end_cond = end_cond
        self.multilaunch = multilaunch
        self.on_startup = on_startup
        self.on_shutdown = on_shutdown
        self.func_run_id = func_run_id
        self.daemon = daemon
        self.batches = batches
        self.permanent = permanent

        # Update name after generation (the local name variable may have been updated)
        # Note: this was moved later to avoid premature hasattr(task, "name") = True during hooks
        # self._name = name  # Will be set after hooks

        # Initialize private attributes
        self._last_run = None
        self._last_success = None
        self._last_fail = None
        self._last_terminate = None
        self._last_inaction = None
        self._last_crash = None
        self._run_stack = []
        self._lock = None
        self._main_alive = False

        # Set up hooks
        hooker = _Hooker(self.session.hooks.task_init)
        hooker.prerun(task=self)

        # Set name after hooks to avoid premature hasattr(task, "name") = True
        self.name = name

        # Run field validation
        self.__post_init__()

        # Validate name in session context
        self._validate_name_in_session()

        # Set default readable logger if missing
        self.session._check_readable_logger()

        self.register()
        self._init_cache()

        # Hooks
        hooker.postrun()

    def _get_name(self, name=None, **kwargs):
        if name is None:
            use_instance_naming = self.session.config.use_instance_naming
            if use_instance_naming:
                return id(self)
            return self.get_default_name(**kwargs)
        return name

    def _validate_name_in_session(self):
        """Validate task name in session context (called from __init__)"""
        if self.session and self.name:
            on_exists = self.session.config.task_pre_exist
            name_exists = self.name in self.session
            if name_exists:
                if on_exists == "ignore":
                    return
                elif on_exists == "raise":
                    raise ValueError(f"Task name '{self.name}' already exists.")
                elif on_exists == "rename":
                    basename = self.name
                    name = self.name
                    num = 0
                    while name in self.session:
                        num += 1
                        name = f"{basename} - {num}"
                    self.name = name

    def __hash__(self):
        return id(self)

    def run(self, _params: Union[Parameters, Dict] = None, **kwargs):
        """Set the task running (with given parameters)

        Creates a run batch that will set the task running
        once. Given parameters are only used once. Can be
        called multiple times to put the task running multiple
        times.


        Parameters
        ----------
        _params : dict, Parameters, optional
            Parameters for the batch
        **kwargs
            Parameters for the batch
        """
        params = Parameters()
        if _params:
            params.update(_params)
        if kwargs:
            params.update(kwargs)
        self.batches.append(params)

    def delete(self):
        """Delete the task from the session.
        Overried if needed additional cleaning."""
        self.session.tasks.remove(self)

    def terminate(self):
        "Terminate the task"
        self.force_termination = True

    # Inspection

    @property
    def is_running(self):
        """bool: Whether the task is currently running or not."""
        return self.get_status() == "run"

    def is_alive(self) -> bool:
        """Whether the task is alive: check if the task has a live process or thread."""
        #! TODO: Use property
        return any(run.is_alive() for run in self._run_stack)

    @property
    def n_alive(self) -> int:
        """int: Number of parallel runs alive."""
        return sum(run.is_alive() for run in self._run_stack)

    # Task Execution

    def __call__(self, *args, **kwargs):
        "Run sync"
        self.start(*args, **kwargs)

    def start(self, *args, **kwargs):
        return asyncio.run(self.start_async(*args, **kwargs))

    async def start_async(self, params: Union[dict, Parameters] = None, **kwargs):
        """Execute the task. Creates a new process
        (if execution='process'), a new thread
        (if execution='thread') or blocks and
        runs till the task is completed (if
        execution='main').

        Parameters
        ----------
        params : dict, Parameters, optional
            Extra parameters for the task. Also
            the session parameters, task parameters
            and extra parameters are acquired, by default None
        """

        # The parameters are handled in the following way:
        #   - First extra parameters are fetched. This includes:
        #       - session.parameters
        #       - _task_, _session_, _thread_terminate_
        #   - Then these extras are prefiltered (called params)
        #   - Then the task parameters are fetched (direct_params)
        #   - If process/thread, these parameters are pre_materialized
        #   - Then the params are post filtered
        #   - Then params and direct_params are fed to the execute method
        execution = self.get_execution()
        task_run = TaskRun(start=self.session.get_time(), task=None)
        try:
            self.force_run = False
            params = self.get_extra_params(params, execution=execution)
            direct_params = self._get_direct_params()

            task_run.run_id = self.get_run_id(task_run, params=params | direct_params)

            # Run the actual task
            if execution in ("main", "async"):
                async_task = asyncio.create_task(
                    self._run_as_async(
                        params=params,
                        direct_params=direct_params,
                        task_run=task_run,
                        execution=execution,
                        **kwargs,
                    )
                )
                if execution == "async":
                    task_run.task = async_task
                self._run_stack.append(task_run)
                self.log_running(task_run)
                if execution == "main":
                    await async_task
                if _IS_WINDOWS:
                    #! TODO: This probably is now solved
                    # There is an annoying bug (?) in Windows:
                    # https://bugs.python.org/issue44831
                    # If one checks whether the task has succeeded/failed
                    # already the log might show that the task finished
                    # 1 microsecond in the future if memory logging is used.
                    # Therefore we sleep that so condition checks especially
                    # in tests will succeed.
                    time.sleep(1e-6)
            elif execution == "process":
                self.run_as_process(
                    params=params,
                    direct_params=direct_params,
                    task_run=task_run,
                    **kwargs,
                )
            elif execution == "thread":
                self.run_as_thread(
                    params=params,
                    direct_params=direct_params,
                    task_run=task_run,
                    **kwargs,
                )
        except (SchedulerRestart, SchedulerExit):
            raise
        except TaskLoggingError:
            if self.status == "run" and execution not in ("thread", "process"):
                # Task logging to run failed
                # so we log it to fail

                # NOTE: processes and threads log independently
                # and it is not aware the logging failed
                # (there is a log record still coming about the finish)
                self.log_failure(task_run)
            raise
        except Exception as exc:
            # Something went wrong in the initiation
            # and it did not reach to log_running
            if task_run.run_id is None:
                task_run.run_id = self.get_run_id(task_run)
            if self.status != "run":
                self.log_running(task_run)
            self.log_failure(task_run)
            raise TaskSetupError("Task failed before logging") from exc
        finally:
            # Clean up
            self._main_alive = False
            # Delete the "main" runs from run stack
            self._run_stack = [run for run in self._run_stack if run.task is not None]

    def __bool__(self):
        return self.is_runnable()

    def is_runnable(self):
        """Check whether the task can be run or not.

        If force_run is True, the task can be run regardless.
        If disabled is True, the task is prevented to be run
        (unless force_true=True).
        If neither of the previous, the start_cond is inspected
        and if it is True, the task can be run.
        """
        # Also add methods:
        #    set_pending() : Set forced_state to False
        #    resume() : Reset forced_state to None
        #    set_running() : Set forced_state to True
        forced_run = bool(self.batches)
        if forced_run:
            return True
        if self.disabled:
            return False

        cond = self.start_cond.observe(task=self)

        return cond

    def run_as_main(self, params: Parameters):
        self.log_running()
        return self._run_as_main(params, direct_params=self.get_task_params())

    def _run_as_main(self, **kwargs):
        return asyncio.run(self._run_as_async(**kwargs))

    async def _run_as_async(
        self,
        params: Parameters,
        direct_params: Parameters,
        task_run: TaskRun,
        execution=None,
        **kwargs,
    ):
        """Run the task on the current thread and process"""
        # NOTE: Assumed that self.log_running() has been already called.
        # (If SystemExit is raised, it won't be catched in except Exception)
        if execution == "process":
            hooks = kwargs.get("hooks", [])
        else:
            hooks = self.session.hooks.task_execute
        hooker = _Hooker(hooks)
        hooker.prerun(task=self)

        status = None
        output = None
        exc_info = (None, None, None)
        params = self.postfilter_params(params)
        params = Parameters(params) | Parameters(direct_params)
        params = params.materialize(task=self, session=self.session)

        try:
            if inspect.iscoroutinefunction(self.execute):
                output = await self.execute(**params)
            else:
                output = self.execute(**params)

            # NOTE: we process success here in case the process_success
            # fails (therefore task fails)
            self.process_success(output)
        except (SchedulerRestart, SchedulerExit):
            # SchedulerRestart is considered as successful task
            self.log_success(task_run)
            status = "succeeded"
            self.process_success(None)
            exc_info = sys.exc_info()
            # Note that these are never silenced
            raise

        except TaskInactionException:
            # Task did not fail, it did not succeed:
            #   The task started but quickly determined was not needed to be run
            #   and therefore the purpose of the task was not executed.
            self.log_inaction(task_run)
            status = "inaction"
            exc_info = sys.exc_info()

        except (TaskTerminationException, asyncio.CancelledError):
            # Task was terminated and the task's function
            # did listen to that.
            self.log_termination(reason="task terminated", task_run=task_run)
            status = "termination"
            exc_info = sys.exc_info()

        except Exception:
            # All the other exceptions (failures)
            try:
                self.process_failure(*sys.exc_info())
            except Exception:
                # Failure of failure processing
                self.log_failure(task_run)
            else:
                self.log_failure(task_run)
            status = "failed"
            # self.logger.error(f'Task {self.name} failed', exc_info=True, extra={"action": "fail"})

            exc_info = sys.exc_info()
            if execution is None:
                raise

        else:
            # Store the output
            if execution != "process":
                self._handle_return(output)
            self.log_success(output, task_run=task_run)
            # self.logger.info(f'Task {self.name} succeeded', extra={"action": "success"})
            status = "succeeded"

            return output

        finally:
            self.process_finish(status=status)
            hooker.postrun(*exc_info)

    def run_as_thread(self, params: Parameters, direct_params, task_run: TaskRun, **kwargs):
        """Create a new thread and run the task on that."""

        terminate_event = params.get("_thread_terminate_", threading.Event())

        params = params.pre_materialize(task=self, session=self.session, terminate_event=terminate_event)
        direct_params = direct_params.pre_materialize(task=self, session=self.session, terminate_event=terminate_event)

        thread = threading.Thread(target=self._run_as_thread, args=(params, direct_params, task_run))
        task_run.task = thread
        task_run.event_terminate = terminate_event
        task_run.event_running = threading.Event()

        self._run_stack.append(task_run)

        self._last_run = self.session.get_time()  # Needed for termination
        thread.start()
        task_run.event_running.wait()  # Wait until the task is confirmed to run

    def _run_as_thread(self, params: Parameters, direct_params: Parameters, task_run: TaskRun = None):
        """Running the task in a new thread. This method should only
        be run by the new thread."""
        try:
            self.log_running(task_run)
        except TaskLoggingError as exc:
            # Logging failed
            task_run.exception = exc
            try:
                self.log_failure()
            except Exception:
                pass
            # Note that we don't raise the error as there is nothing
            # to catch it
            return
        finally:
            task_run.event_running.set()

        try:
            output = self._run_as_main(
                params=params,
                direct_params=direct_params,
                task_run=task_run,
                execution="thread",
            )
        except Exception:
            # Task crashed before actually running the execute.
            try:
                self.log_failure()
            except TaskLoggingError as exc:
                task_run.exception = exc

            # We cannot rely the exception to main thread here
            # thus we supress to prevent unnecessary warnings.

    def run_as_process(
        self,
        params: Parameters,
        direct_params: Parameters,
        task_run: TaskRun,
        daemon=None,
        log_queue: multiprocessing.Queue = None,
    ):
        """Create a new process and run the task on that."""

        session = self.session

        params = params.pre_materialize(task=self, session=session)
        direct_params = direct_params.pre_materialize(task=self, session=session)

        # Daemon resolution: task.daemon >> scheduler.tasks_as_daemon
        log_queue = session.scheduler._log_queue if log_queue is None else log_queue

        daemon = self.daemon if self.daemon is not None else session.config.tasks_as_daemon
        process = multiprocessing.Process(
            target=self._run_as_process,
            kwargs=dict(
                params=params,
                direct_params=direct_params,
                task_run=task_run,
                queue=log_queue,
                config=session.config,
                exec_hooks=self._get_hooks("task_execute"),
            ),
            daemon=daemon,
        )
        task_run.task = process

        self._run_stack.append(task_run)
        self._mark_running = True  # needed in pickling
        process.start()
        self._mark_running = False

        self._lock_to_run_log(log_queue)
        return log_queue

    def _run_as_process(
        self,
        params: Parameters,
        direct_params: Parameters,
        task_run,
        queue,
        config,
        exec_hooks,
    ):
        """Running the task in a new process. This method should only
        be run by the new process."""

        # NOTE: This is in the process and other info in the application
        # cannot be accessed here. Self is a copy of the original
        # and cannot affect main processes' attributes!

        # The task's logger has been removed by MultiScheduler.run_task_as_process
        # (see the method for more info) and we need to recreate the logger now
        # in the actual multiprocessing's process. We only add QueueHandler to the
        # logger (with multiprocessing.Queue as queue) so that all the logging
        # records end up in the main process to be logged properly.
        basename = self.logger_name
        # handler = logging.handlers.QueueHandler(queue)
        handler = QueueHandler(queue)

        # Set the process logger
        logger = logging.getLogger(basename + "._process")
        logger.setLevel(logging.INFO)
        logger.propagate = False
        logger.handlers = []
        logger.addHandler(handler)
        # Wrap logger.createRecord for custom created time
        self.session._wrap_log_record_creation(logger)
        try:
            self.logger_name = logger.name
        except:
            logger.critical(
                f"Task '{self.name}' crashed in setting up logger.",
                exc_info=True,
                extra={"action": "fail", "task_name": self.name},
            )
            raise
        self.log_running(task_run)
        try:
            # NOTE: The parameters are "materialized"
            # here in the actual process that runs the task
            output = self._run_as_main(
                params=params,
                direct_params=direct_params,
                task_run=task_run,
                execution="process",
                hooks=exec_hooks,
            )
        except Exception as exc:
            # Task crashed before running execute (silence=True)
            self.log_failure()

            # There is nothing to raise it
            # to :(
            pass

    def get_extra_params(self, params: Parameters, execution: str, **kwargs) -> Parameters:
        """Get additional parameters

        Returns
        -------
        Parameters
            Additional parameters
        """
        passed_params = Parameters(params)
        session_params = self.session.parameters
        extra_params = Parameters(_session_=self.session, _task_=self, **kwargs)
        if execution == "thread":
            extra_params["_thread_terminate_"] = threading.Event()

        params = Parameters(self.prefilter_params(session_params | passed_params | extra_params))

        return params

    def _get_direct_params(self):
        direct_params = self.get_task_params()
        if self.batches:
            direct_params.update(self.batches.pop(0))
        return direct_params

    def get_task_params(self):
        "Get parameters passed to the task"
        return self.parameters.copy()

    def prefilter_params(self, params: Parameters):
        """Pre filter the parameters.

        This method filters the task parameters before
        a thread or a process is created. This method
        always called in the main process and in the
        main thread. Therefore, one can filter here the
        parameters that are problematic to pass to a
        thread or process.

        Parameters
        ----------
        params : tocketry.core.Parameters

        Returns
        -------
        Parameters : dict, tocketry.core.Parameters
            Filtered parameters.
        """
        return filter_keyword_args(self.execute, params)

    def postfilter_params(self, params: Parameters):
        """Post filter the parameters.

        This method filters the task parameters after
        a thread or a process is created. This method
        called in the child process, if ``execution='process'``,
        or in the child thread ``execution='thread'``.
        For ``execution='main'``, overriding this method
        does not have much impact over overriding
        ``prefilter_params``.

        Parameters
        ----------
        params : tocketry.core.Parameters

        Returns
        -------
        Parameters : dict, tocketry.core.Parameters
            Filtered parameters.
        """
        return params

    @abstractmethod
    def execute(self, *args, **kwargs):
        """Run the actual task. Override this.

        Parameters are materialized to keyword arguments.
        """
        raise NotImplementedError(f"Method 'execute' not implemented to {type(self)}.")

    def process_failure(self, exc_type: Type[Exception], exc_val: Exception, exc_tb: TracebackType):
        """This method is executed after a failure of the task.
        Override if needed.

        Parameters
        ----------
        exc_type : subclass of Exception
            Type of the occurred exception that caused the failure.
        exc_val : Exception
            Exception that caused the failure.
        exc_type : Traceback object
            Traceback of the failure exception.
        """
        pass

    def process_success(self, output: Any):
        """This method is executed after a success of the task.
        Override if needed.

        Parameters
        ----------
        output : Any
            Return value of the task.
        """
        pass

    def process_finish(self, status: str):
        """This method is executed after finishing the task.
        Override if needed.

        Parameters
        ----------
        status : str {'succeeded', 'failed', 'termination', 'inaction'}
            How the task finished.
        """
        pass

    def register(self):
        if hasattr(self, "_mark_register") and not self._mark_register:
            del self._mark_register
            return  # on_exists = 'ignore'
        name = self.name
        self.session.add_task(self)

    def _init_cache(self):
        self._last_run = None
        self._last_success = None
        self._last_fail = None
        self._last_terminate = None
        self._last_inaction = None
        self._last_crash = None

    def set_cached(self):
        "Update cached statuses"
        # We get the logger here to not flood with warnings if missing repo
        logger = self.logger

        self._last_run = self._get_last_action("run", from_logs=True, logger=logger)
        self._last_success = self._get_last_action("success", from_logs=True, logger=logger)
        self._last_fail = self._get_last_action("fail", from_logs=True, logger=logger)
        self._last_terminate = self._get_last_action("terminate", from_logs=True, logger=logger)
        self._last_inaction = self._get_last_action("inaction", from_logs=True, logger=logger)
        self._last_crash = self._get_last_action("crash", from_logs=True, logger=logger)

        times = {
            name: getattr(self, f"_last_{name}")
            for name in ("run", "success", "fail", "terminate", "inaction", "crash")
            if getattr(self, f"_last_{name}") is not None
        }
        if times:
            status = max(times, key=times.get)
            if status == "run":
                # There has been a sudden crash
                self.log_crash()
            else:
                self.status = status

    def get_default_name(self, **kwargs):
        """Create a name for the task when name was not passed to initiation of
        the task. Override this method."""
        raise NotImplementedError(f"Method 'get_default_name' not implemented to {type(self)}")

    def get_run_id(self, run, params=None):
        if self.func_run_id is not None:
            return self.func_run_id(self, params)
        return self.session.config.func_run_id(self, params)

    def is_alive_as_main(self) -> bool:
        return any(run.is_main and run.is_alive() for run in self._run_stack)

    def is_alive_as_async(self) -> bool:
        return any(run.is_async and run.is_alive() for run in self._run_stack)

    def is_alive_as_thread(self) -> bool:
        """Whether the task has a live thread."""
        return any(run.is_thread and run.is_alive() for run in self._run_stack)

    def is_alive_as_process(self) -> bool:
        """Whether the task has a live process."""
        return any(run.is_process and run.is_alive() for run in self._run_stack)

    def count_processes_taken(self) -> int:
        """Count number of processes the task takes"""
        return sum(run.is_process and run.is_alive() for run in self._run_stack)

    async def _check_termination(self):
        "Terminate task if can"
        try:
            is_end_cond = self.end_cond.observe(task=self, session=self.session)
        except Exception:
            if not self.session.config.silence_cond_check:
                raise
            is_end_cond = True

        if self.force_termination:
            await self._terminate_all(reason="forced termination")
        elif is_end_cond:
            await self._terminate_all(reason="end condition is true")
        else:
            now = self.session.get_time()
            if self.permanent:
                return
            timeout = self.timeout if self.timeout else self.session.config.timeout
            timeout_sec = timeout.total_seconds()
            for run in self._run_stack:
                start = run.start
                run_duration = now - start
                if run.is_alive() and run_duration > timeout_sec:
                    await self._terminate_run(run, reason="timeouted")

    def _clean_run_stack(self):
        "Remove dead runs from run stack"
        if self.session.config.silence_task_logging:
            self._run_stack = [run for run in self._run_stack if run.is_alive()]
        else:
            self._run_stack = [run for run in self._run_stack if run.is_alive() or run.exception is not None]

    def _check_exceptions(self):
        for run in self._run_stack.copy():
            if run.exception:
                self._run_stack.remove(run)
                raise run.exception

    async def _terminate_all(self, reason=None):
        "Terminate the whole run stack"
        for run in self._run_stack:
            await self._terminate_run(run, reason=reason)
        self._clean_run_stack()
        self.force_termination = False
        # self._run_stack = [] # Does not work with threads

    async def _terminate_run(self, run: TaskRun, reason=None):
        "Terminate the whole run stack"
        try:
            await run.terminate()
        except asyncio.CancelledError:
            # Async tasks raise CancelledError if terminated
            self.log_termination(reason=reason, task_run=run)
        else:
            if run.is_process:
                # Threaded tasks handle their termination themselves
                self.log_termination(reason=reason, task_run=run)

    # Logging
    def _lock_to_run_log(self, log_queue):
        "Handle next run log to make sure the task started running before continuing (otherwise may cause accidential multiple launches)"
        action = None
        timeout = 10  # Seconds allowed the setup to take before declaring setup to crash

        # NOTE: The queue may return others task logs as well
        # but the next run log should be only from this task
        # as log_running is part of the task startup process.

        err = None

        while action != "run":
            try:
                record = log_queue.get(block=True, timeout=timeout)
            except Empty:
                if not self.is_alive():
                    # There will be no "run" log record thus ending the task gracefully
                    self.logger.critical(f"Task '{self.name}' crashed in setup", extra={"action": "fail"})
                    raise TaskSetupError(f"Task '{self.name}' process crashed silently")
            else:
                # self.logger.debug(f"Inserting record for '{record.task_name}' ({record.action})")
                task = self.session[record.task_name]
                try:
                    task.log_record(record)
                except Exception as exc:
                    # It must be made sure the task is set running
                    # so we ignore logging errors until that's sure
                    err = exc

                action = record.action

        if err is not None:
            raise err

    def log_running(self, task_run: TaskRun = None):
        """Make a log that the task is currently running."""
        self._set_status("run", task_run)

    def log_failure(self, task_run: TaskRun = None):
        """Log that the task failed."""
        self._set_status("fail", task_run)

    def log_success(self, return_value=None, task_run: TaskRun = None):
        """Make a log that the task succeeded."""
        self._set_status("success", task_run, return_value=return_value)
        # self.status = "success"

    def log_termination(self, reason=None, task_run: TaskRun = None):
        """Make a log that the task was terminated."""
        reason = reason or "unknown reason"
        msg = self.fmt_log_message.format(action="terminate", task=self.name)
        self._set_status("terminate", task_run, message=msg + f" ({reason})")

        # Reset event and force_termination (for threads)
        self.force_termination = False

    def log_inaction(self, task_run: TaskRun = None):
        """Make a log that the task did nothing."""
        self._set_status("inaction", task_run)

    def log_crash(self, task_run: TaskRun = None):
        """Make a log that the task had previously crashed"""
        self._set_status("crash", task_run)

    def log_record(self, record: logging.LogRecord):
        """Log the record with the logger of the task.
        Also sets the status according to the record.
        """
        # Set last_run/last_success/last_fail etc.
        cache_attr = f"_last_{record.action}"
        record_time = record.created

        try:
            self.logger.handle(record)
        except Exception as exc:
            if record.action == "run":
                # The task started and the run must be set
                # even though the task partly failed already
                setattr(self, cache_attr, record_time)
                self.status = record.action
            else:
                # Logging is part of the task so even if the task
                # function itself succeeded, the task failed
                setattr(self, "_last_fail", record_time)
                self.status = "fail"
            
            # Only raise the exception if not silencing task logging
            if not self.session.config.silence_task_logging:
                raise TaskLoggingError(f"Logging for task '{self.name}' failed.") from exc
        else:
            setattr(self, cache_attr, record_time)
            self.status = record.action

    def get_status(
        self,
    ) -> Literal["run", "fail", "success", "terminate", "inaction", None]:
        """Get latest status of the task."""
        if self.session.config.force_status_from_logs:
            try:
                record = self.logger.get_latest()
            except AttributeError:
                if is_main_subprocess():
                    warnings.warn(f"Task '{self.name}' logger is not readable. Status unknown.")
                record = None
            if not record:
                # No previous status
                return None
            status = record["action"] if isinstance(record, dict) else record.action
            self.status = status
            return status
        # This is way faster
        return self.status

    def _set_status(self, action, task_run: TaskRun = None, message=None, return_value=None):
        if message is None:
            message = self.fmt_log_message.format(action=action, task=self.name)

        if action not in self._actions:
            raise KeyError(f"Invalid action: {action}")

        time_now = self.session.get_time()

        if action == "run":
            extra = {
                "action": "run",
                "start": task_run.start if task_run is not None else time_now,
            }
            # self._last_run = now
        else:
            start_time = self._get_last_action("run")
            runtime = time_now - start_time if start_time is not None else None
            extra = {
                "action": action,
                "start": start_time,
                "end": time_now,
                "runtime": runtime,
            }

        extra["run_id"] = task_run.run_id if task_run is not None else None

        is_running_as_child = self.logger.name.endswith("._process")
        if is_running_as_child and action == "success":
            # If child process, the return value is passed via QueueHandler to the main process
            # and it's handled then in Scheduler.
            # Else the return value is handled in Task itself (__call__ & _run_as_thread)
            extra["__return__"] = return_value

        cache_attr = f"_last_{action}"

        log_method = self.logger.exception if action == "fail" else self.logger.info
        try:
            log_method(message, extra=extra)
        except Exception as exc:
            if action == "run":
                setattr(self, cache_attr, time_now)
                self.status = action
            else:
                setattr(self, "_last_fail", time_now)
                self.status = "fail"
            
            # Only raise the exception if not silencing task logging
            if not self.session.config.silence_task_logging:
                raise TaskLoggingError(f"Logging for task '{self.name}' failed.") from exc
        else:
            setattr(self, cache_attr, time_now)
            self.status = action

    def get_last_success(self) -> datetime.datetime:
        """Get the lastest timestamp when the task succeeded."""
        time = self._get_last_action("success")
        if time is not None:
            time = self.session._format_timestamp(time)
        return time

    def get_last_fail(self) -> datetime.datetime:
        """Get the lastest timestamp when the task failed."""
        time = self._get_last_action("fail")
        if time is not None:
            time = self.session._format_timestamp(time)
        return time

    def get_last_run(self) -> datetime.datetime:
        """Get the lastest timestamp when the task ran."""
        time = self._get_last_action("run")
        if time is not None:
            time = self.session._format_timestamp(time)
        return time

    def get_last_terminate(self) -> datetime.datetime:
        """Get the lastest timestamp when the task terminated."""
        time = self._get_last_action("terminate")
        if time is not None:
            time = self.session._format_timestamp(time)
        return time

    def get_last_inaction(self) -> datetime.datetime:
        """Get the lastest timestamp when the task inacted."""
        time = self._get_last_action("inaction")
        if time is not None:
            time = self.session._format_timestamp(time)
        return time

    def get_last_crash(self) -> datetime.datetime:
        """Get the lastest timestamp when the task inacted."""
        time = self._get_last_action("crash")
        if time is not None:
            time = self.session._format_timestamp(time)
        return time

    def get_execution(self) -> str:
        if self.execution is None:
            return self.session.config.execution
        return self.execution

    def _get_last_action(self, action: str, from_logs=None, logger=None) -> float:
        cache_attr = f"_last_{action}"
        if from_logs is not None:
            allow_cache = not from_logs
        else:
            if self.session is None:
                allow_cache = True
            else:
                allow_cache = not self.session.config.force_status_from_logs

        if allow_cache:  #  and getattr(self, cache_attr) is not None
            value = getattr(self, cache_attr, None)
        else:
            value = self._get_last_action_from_log(action, logger)
            setattr(self, cache_attr, value)
        return value

    def _get_last_action_from_log(self, action, logger=None):
        """Get last action timestamp from log"""
        logger = logger if logger is not None else self.logger
        try:
            record = logger.get_latest(action=action)
        except AttributeError:
            if is_main_subprocess():
                warnings.warn(f"Task '{self.name}' logger is not readable. Latest {action} unknown.")
            return None
        else:
            if not record:
                return None
            timestamp = record["created"] if isinstance(record, dict) else record.created
            return timestamp

    def __getstate__(self):
        # # capture what is normally pickled
        # state = self.__dict__.copy()
        #
        # # remove unpicklable
        # # TODO: Include conditions by enforcing tasks are passed to the conditions as names
        # state['_logger'] = None
        # state['_start_cond'] = None
        # state['_end_cond'] = None
        # #state["_process"] = None # If If execution == "process"
        # #state["_thread"] = None # If execution == "thread"
        #
        # state["_lock"] = None # Process task cannot lock anything anyways

        # capture what is normally pickled
        state = self.__dict__.copy()

        # remove unpicklable attributes
        state["_lock"] = None
        state["_process"] = None
        state["_thread"] = None
        state["_run_stack"] = None

        # We also get rid of the conditions as if there is a task
        # containing an attr that cannot be pickled (like FuncTask
        # containing lambda function but ran as main/thread), we
        # would face sudden crash.
        state["start_cond"] = None
        state["end_cond"] = None

        # Removing possibly unpicklable manually. There is a problem in Pydantic
        # and for some reason it does not use Session's pickling
        state["parameters"] = Parameters()
        state["session"] = state["session"]._copy_pickle()

        if not is_pickleable(state):
            if self._mark_running:
                # When this block might get executed?
                #   - If FuncTask func is non-picklable
                #       - There is another func with same name in the file
                #       - The function is lambda or decorated func
                unpicklable = {key: val for key, val in state.items() if not is_pickleable(val)}
                self.log_running()
                self.logger.critical(
                    f"Task '{self.name}' crashed in pickling. Cannot pickle: {unpicklable}",
                    extra={"action": "fail", "task_name": self.name},
                )
                raise PicklingError(f"Task {self.name} could not be pickled. Cannot pickle: {unpicklable}")
            # Is pickled by something else than task execution
            return state

        # what we return here will be stored in the pickle
        return state

    def _handle_return(self, value):
        "Handle the return value (ie. store to parameters)"
        self.session.returns[self] = value

    def _get_hooks(self, name: str):
        return getattr(self.session.hooks, name)

    # Other
    @property
    def period(self) -> TimePeriod:
        """TimePeriod: Time period in which the task runs

        Note that this should not be considered as absolute truth but
        as a best estimate.
        """
        from tocketry.core.time import StaticInterval, All as AllTime
        from tocketry.conditions import TaskFinished, TaskSucceeded

        cond = self.start_cond
        session = self.session

        if isinstance(cond, (TaskSucceeded, TaskFinished)):
            if session[cond.kwargs["task"]] is self:
                return cond.period

        elif isinstance(cond, All):
            task_periods = []
            for sub_stmt in cond:
                if isinstance(sub_stmt, (TaskFinished, TaskFinished)) and session[sub_stmt.kwargs["task"]] is self:
                    task_periods.append(sub_stmt.period)
            if task_periods:
                return AllTime(*task_periods)

        # TimePeriod could not be determined
        return StaticInterval()

    @property
    def lock(self):
        # Lock is private in a sense that we want to hide it from
        # the model (if put to dict etc.) but public in a sense
        # that the user should be allowed to interact with it
        if self._lock is None:
            self._lock = self.session.config.cls_lock()
        return self._lock

    @property
    def last_run(self):
        return self.get_last_run()

    @property
    def last_success(self):
        return self.get_last_success()

    @property
    def last_fail(self):
        return self.get_last_fail()

    @property
    def last_terminate(self):
        return self.get_last_terminate()

    @property
    def last_crash(self):
        return self.get_last_crash()

    @property
    def last_inaction(self):
        return self.get_last_inaction()

    def model_dump(self, exclude=None, **kwargs):
        """Compatibility method to replace pydantic's model_dump"""
        from dataclasses import fields
        from collections import OrderedDict

        # Define the expected field order to match the original pydantic output
        expected_order = [
            "permanent", "fmt_log_message", "daemon", "batches", "name", "description", 
            "logger_name", "execution", "priority", "disabled", "force_run", 
            "force_termination", "status", "timeout", "parameters", "start_cond", 
            "end_cond", "multilaunch", "on_startup", "on_shutdown", "func_run_id"
        ]

        # Get data from dataclass fields that exist as attributes
        field_data = {}
        for field in fields(self):
            if not field.name.startswith("_"):  # Exclude private fields
                # Check if the attribute was explicitly deleted by checking __dict__
                if field.name in self.__dict__:
                    value = getattr(self, field.name)
                    field_data[field.name] = value
                elif hasattr(self, field.name):
                    # Include fields with default values that weren't explicitly set
                    value = getattr(self, field.name)
                    if value is not None or field.default is not None:
                        field_data[field.name] = value

        # Add special fields that aren't dataclass fields but should be in JSON
        # These were moved out of dataclass fields but need to appear in serialization
        if hasattr(self, 'name'):
            field_data['name'] = self.name
        if hasattr(self, '_force_run'):
            field_data['force_run'] = self._force_run
        if hasattr(self, '_status'):
            field_data['status'] = self._status

        # Create ordered dict based on expected order
        data = OrderedDict()
        for field_name in expected_order:
            if field_name in field_data:
                data[field_name] = field_data[field_name]
        
        # Add any remaining fields that weren't in the expected order (shouldn't happen normally)
        for field_name, value in field_data.items():
            if field_name not in data:
                data[field_name] = value

        # Remove excluded fields
        if exclude:
            if isinstance(exclude, set):
                exclude = list(exclude)
            for field in exclude:
                data.pop(field, None)

        # Special handling for parameters to match pydantic format
        if "parameters" in data and hasattr(data["parameters"], "_params"):
            # Convert Parameters object to dict like pydantic did
            params = data["parameters"]
            param_dict = {}
            for k, v in params._params.items():
                try:
                    # Use repr() for arguments to match pydantic format
                    param_dict[k] = repr(v)
                except Exception:
                    # If we can't repr the value, use str
                    param_dict[k] = str(v)
            data["parameters"] = param_dict
        elif "parameters" in data and hasattr(data["parameters"], "__dict__"):
            # Fallback for other parameter-like objects
            params = data["parameters"]
            param_dict = {}
            for k, v in params.__dict__.items():
                if not k.startswith("_"):
                    param_dict[k] = str(v)
            data["parameters"] = param_dict

        # Convert back to regular dict for JSON serialization
        return dict(data)

    def model_dump_json(self, exclude=None, indent=None, **kwargs):
        """Compatibility method to replace pydantic's model_dump_json"""
        import json

        data = self.model_dump(exclude=exclude, **kwargs)

        # Convert non-serializable objects to strings
        def serialize_obj(obj):
            if hasattr(obj, "__dict__"):
                return str(obj)
            elif hasattr(obj, "__name__"):
                return obj.__name__
            else:
                return str(obj)

        # Handle complex objects that can't be JSON serialized
        def clean_for_json(data):
            if isinstance(data, dict):
                return {k: clean_for_json(v) for k, v in data.items()}
            elif isinstance(data, list):
                return [clean_for_json(v) for v in data]
            elif hasattr(data, "__dict__") or callable(data):
                return serialize_obj(data)
            else:
                try:
                    json.dumps(data)  # Test if it's JSON serializable
                    return data
                except (TypeError, ValueError):
                    return serialize_obj(data)

        clean_data = clean_for_json(data)
        return json.dumps(clean_data, indent=indent, default=str)

    def json(self, **kwargs):
        if "exclude" not in kwargs:
            kwargs["exclude"] = set()
        kwargs["exclude"].update({"session"})
        return self.model_dump_json(**kwargs)
