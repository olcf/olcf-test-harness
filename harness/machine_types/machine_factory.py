# Python system imports
import os
import sys

# Local package imports
from .linux_x86_64 import Linux_x86_64
from .machine_factory_exceptions import MachineTypeNotImplementedError
from .machine_factory_exceptions import MachineTypeUndefinedVariableError

class MachineFactory:

    def __init__(self):
        return

    @staticmethod
    def create_machine(harness_config,
                       app_subtest,
                       separate_build_stdio=False):

        # Uses the app_subtest's logger to print errors
        machine_config = harness_config.get_machine_config()

        # Verify that the machine configuration variables 'machine_name',
        # and 'scheduler_type' are defined.
        # Otherwise throw an exception and stop.
        rgt_machine_name = None
        rgt_machine_type = None
        rgt_scheduler = None
        try:
            rgt_machine_name = machine_config.get('machine_name')
            if rgt_machine_name == None:
                app_subtest.logger.doCriticalLogging('No machine name provided by harness configuration!')
                raise MachineTypeUndefinedVariableError("MachineDetails.machine_name")

            rgt_machine_type = machine_config.get('machine_type')
            if rgt_machine_type == None:
                app_subtest.logger.doCriticalLogging('No machine type provided by harness configuration!')
                raise MachineTypeUndefinedVariableError("MachineDetails.machine_type")

            rgt_scheduler = machine_config.get('scheduler_type')
            if rgt_scheduler == None:
                app_subtest.logger.doCriticalLogging('No scheduler type provided by harness configuration!')
                raise MachineTypeUndefinedVariableError("MachineDetails.scheduler_type")

        except MachineTypeUndefinedVariableError as my_exception:
            my_exception.what()
            sys.exit()

        rgt_num_nodes = machine_config.get('node_count')
        if rgt_num_nodes == None:
            rgt_num_nodes = 1

        rgt_cores_per_node = machine_config.get('cpus_per_node')
        if rgt_cores_per_node == None:
            rgt_cores_per_node = 1

        rgt_sockets_per_node = machine_config.get('sockets_per_node')
        if rgt_sockets_per_node == None:
            rgt_sockets_per_node = 1

        rgt_cores_per_socket = int(rgt_cores_per_node) / int(rgt_sockets_per_node)

        message = f'Creating machine {rgt_machine_name}: Type = {rgt_machine_type} ; Scheduler = {rgt_scheduler}'
        app_subtest.logger.doInfoLogging(message)

        # We now create a new machine. If the new machine type is not implemented,
        # then warn user, throw an exception and stop.
        tmp_machine = None
        try:
            if rgt_machine_type == "linux_x86_64":
                tmp_machine = Linux_x86_64(name=rgt_machine_name,
                                           scheduler=rgt_scheduler,
                                           numNodes=int(rgt_num_nodes),
                                           numSocketsPerNode=int(rgt_sockets_per_node),
                                           numCoresPerSocket=int(rgt_cores_per_socket),
                                           separate_build_stdio=separate_build_stdio,
                                           apptest=app_subtest)
            else:
                raise MachineTypeNotImplementedError(rgt_machine_type)
        except MachineTypeNotImplementedError as my_exception:
            my_exception.what()
            sys.exit()

        return tmp_machine

