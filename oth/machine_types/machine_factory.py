# Python system imports
import os
import sys

# Local package imports
from .linux_x86_64 import Linux_x86_64

class MachineFactory:

    def __init__(self):
        return

    @staticmethod
    def create_machine(app_subtest,
                       separate_build_stdio=False):

        # Uses the app_subtest's logger to print errors
        from oth.config import othctl_runtime_config
        rgt_machine_name = othctl_runtime_config.machine_name
        rgt_machine_type = othctl_runtime_config.machine_type
        rgt_scheduler = othctl_runtime_config.scheduler_type

        message = f'Creating machine {rgt_machine_name}: Type = {rgt_machine_type} ; Scheduler = {rgt_scheduler}'
        app_subtest.logger.log_info(message)

        tmp_machine = None
        if rgt_machine_type == "linux_x86_64":
            tmp_machine = Linux_x86_64(name=rgt_machine_name,
                                        scheduler=rgt_scheduler,
                                        separate_build_stdio=separate_build_stdio,
                                        apptest=app_subtest)
        else:
            raise ValueError(f"Invalid machine type: {rgt_machine_type}")

        return tmp_machine

