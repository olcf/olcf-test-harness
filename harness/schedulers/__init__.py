from libraries.output_hub import OutputHub

from .base import SchedulerJob
from .lsf import LSF
from .pbs import PBS
from .slurm import Slurm


def create_scheduler(_type: str, logger: OutputHub, use_jinja2=False):
    scheduler = None

    if _type.upper() == "LSF":
        scheduler = LSF(logger, use_jinja2)
    elif _type.upper() == "SLURM":
        scheduler = Slurm(logger, use_jinja2)
    elif _type.upper() == "PBS":
        scheduler = PBS(logger, use_jinja2)
    else:
        logger.log_critical("Scheduler not supported. Good bye!")

    return scheduler


__all__ = [
    SchedulerJob,
    create_scheduler,
]
