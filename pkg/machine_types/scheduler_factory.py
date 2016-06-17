import os
from .lsf import LSF
from .pbs import PBS

class SchedulerFactory:

    @staticmethod
    def create_scheduler(scheduler_type):
        print("Creating scheduler")

        tmp_scheduler = None
        if scheduler_type == "LSF":
            tmp_scheduler = LSF()
        elif scheduler_type == "PBS":
            tmp_scheduler = PBS()
        else:
            print("Scheduler not supported. Good bye!")

        return tmp_scheduler


    def __init__(self):
        pass

