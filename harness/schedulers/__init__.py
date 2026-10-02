from typing import Optional

from harness.libraries.output_hub import OutputHub

from .base import BaseScheduler, SchedulerJob
from .lsf import LSF
from .pbs import PBS
from .slurm import Slurm


def create_scheduler(_type: str, logger: OutputHub, use_jinja2=False) -> BaseScheduler:
    scheduler: Optional[BaseScheduler] = None

    if _type.upper() == "LSF":
        scheduler = LSF(logger, use_jinja2)
    elif _type.upper() == "SLURM":
        scheduler = Slurm(logger, use_jinja2)
    elif _type.upper() == "PBS":
        scheduler = PBS(logger, use_jinja2)
    else:
        logger.log_critical("Scheduler not supported. Good bye!")
        raise TypeError(f"scheduler type {_type} is not supported")

    return scheduler


__all__ = [
    "SchedulerJob",
    "create_scheduler",
]
