import os
from .lsf import LSF
from .pbs import PBS
from .slurm import SLURM

class SchedulerFactory:

    @staticmethod
    def create_scheduler(scheduler_type, logger, use_jinja2=False):
        tmp_scheduler = None
        if scheduler_type == "LSF" or scheduler_type == "lsf":
            tmp_scheduler = LSF(logger=logger, use_jinja2=use_jinja2)
        elif scheduler_type == "SLURM" or scheduler_type == "slurm":
            tmp_scheduler = SLURM(logger=logger, use_jinja2=use_jinja2)
        elif scheduler_type == "PBS" or scheduler_type == "pbs":
            tmp_scheduler = PBS(logger=logger, use_jinja2=use_jinja2)
        else:
            logger.doCriticalLogging("Scheduler not supported. Good bye!")
        return tmp_scheduler

    def __init__(self):
        pass

