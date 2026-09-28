from libraries.output_hub import OutputHub

from .base import SchedulerJob
from .slurm import Slurm


def create_scheduler(_type: str, logger: OutputHub, use_jinja2=False):
    scheduler = None

    if _type.upper() == "SLURM":
        scheduler = Slurm(logger, use_jinja2)

    return scheduler


__all__ = [
    SchedulerJob,
    create_scheduler,
]
