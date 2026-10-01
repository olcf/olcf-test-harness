import os
import re
from abc import ABC, abstractmethod
from typing import Optional

from libraries.output_hub import OutputHub


class SchedulerJob(ABC):
    """Scheduler job class."""

    def __init__(self, batch_script: str, id: Optional[str] = None):
        self.batch_script: str = batch_script
        self.id: Optional[str] = id


class BaseScheduler(ABC):
    """Base scheduler class."""

    name: str = "BaseScheduler"
    submit_executable: str = "echo"
    submit_stdout_file: str = "submit.out"
    submit_stderr_file: str = "submit.err"
    job_id_regex = re.compile(
        r"\d+"
    )  # Python 3.6 does not have a public type for a compiled regex

    def __init__(self, logger: OutputHub, use_jinja2: bool = False):
        self._logger: OutputHub = logger
        self._use_jinja2: bool = use_jinja2

    def _setup_job_env(self) -> None:
        if "SHLVL" in os.environ:
            # Fixes issue #181
            os.environ["SHLVL"] = "1"

    @property
    def batch_script_template_file(self) -> str:
        if self._use_jinja2:
            return f"{self.__class__.__name__.lower()}.template.j2"
        return f"{self.__class__.__name__.lower()}.template.x"

    @abstractmethod
    def submit_job(self, job: SchedulerJob) -> int:
        pass
