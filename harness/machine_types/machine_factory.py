# Python system imports
import os
import sys

# Local package imports
from .ibm_power9 import IBMpower9
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

        machine_config = harness_config.get_machine_config()

        # Verify that the machine configuration variables 'machine_name',
        # 'scheduler_type', and 'joblauncher_type' are defined.
        # Otherwise throw an exception and stop.
        rgt_machine_name = None
        rgt_machine_type = None
        rgt_scheduler = None
        rgt_launcher = None
        try:
            rgt_machine_name = machine_config.get('machine_name')
            if rgt_machine_name == None:
                print('No machine name provided by harness configuration!')
                raise MachineTypeUndefinedVariableError("MachineDetails.machine_name")

            rgt_machine_type = machine_config.get('machine_type')
            if rgt_machine_type == None:
                print('No machine type provided by harness configuration!')
                raise MachineTypeUndefinedVariableError("MachineDetails.machine_type")

            rgt_scheduler = machine_config.get('scheduler_type')
            if rgt_scheduler == None:
                print('No scheduler type provided by harness configuration!')
                raise MachineTypeUndefinedVariableError("MachineDetails.scheduler_type")

            rgt_launcher = machine_config.get('joblauncher_type')
            if rgt_launcher == None:
                print('No scheduler type provided by harness configuration!')
                raise MachineTypeUndefinedVariableError("MachineDetails.joblauncher_type")

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

        message = f'Creating machine {rgt_machine_name}: Type = {rgt_machine_type} ; Scheduler = {rgt_scheduler} ; Job launcher = {rgt_launcher}'
        print(message)

        # We now create a new machine. If the new machine type is not implemented,
        # then warn user, throw an exception and stop.
        tmp_machine = None
        try:
            if rgt_machine_type == "ibm_power9":
                tmp_machine = IBMpower9(name=rgt_machine_name,
                                        scheduler=rgt_scheduler,
                                        jobLauncher=rgt_launcher,
                                        numNodes=int(rgt_num_nodes),
                                        numSocketsPerNode=int(rgt_sockets_per_node),
                                        numCoresPerSocket=int(rgt_cores_per_socket),
                                        separate_build_stdio=separate_build_stdio,
                                        apptest=app_subtest)
            elif rgt_machine_type == "linux_x86_64":
                tmp_machine = Linux_x86_64(name=rgt_machine_name,
                                           scheduler=rgt_scheduler,
                                           jobLauncher=rgt_launcher,
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

