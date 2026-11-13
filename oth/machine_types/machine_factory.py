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
        oth_machine_name = othctl_runtime_config.machine_name
        oth_machine_type = othctl_runtime_config.machine_type
        oth_scheduler = othctl_runtime_config.scheduler_type

        message = f'Creating machine {oth_machine_name}: Type = {oth_machine_type} ; Scheduler = {oth_scheduler}'
        app_subtest.logger.log_info(message)

        tmp_machine = None
        if oth_machine_type == "linux_x86_64":
            tmp_machine = Linux_x86_64(name=oth_machine_name,
                                        scheduler=oth_scheduler,
                                        separate_build_stdio=separate_build_stdio,
                                        apptest=app_subtest)
        else:
            raise ValueError(f"Invalid machine type: {oth_machine_type}")

        return tmp_machine

