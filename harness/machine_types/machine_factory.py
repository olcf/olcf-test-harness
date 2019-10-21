# Python system imports
import os
import sys

# Local package imports
from .cray_xk7 import CrayXK7
from .ibm_power8 import IBMpower8
from .ibm_power9 import IBMpower9
from .rhel_x86 import RHELx86
from .machine_factory_exceptions import MachineTypeNotImplementedError
from .machine_factory_exceptions import MachineTypeUndefinedEnvironmentalVariableError

class MachineFactory:

    def __init__(self):
        return

    @staticmethod
    def create_machine(path_to_workspace,
                       harness_id):
        rgt_machine_name = os.environ.get("RGT_MACHINE_NAME")
        rgt_scheduler_type = os.environ.get("RGT_SCHEDULER_TYPE")
        rgt_jobLauncher_type = os.environ.get("RGT_JOBLAUNCHER_TYPE")
        rgt_path_to_workspace = path_to_workspace
        rgt_harness_id = harness_id
        rgt_scripts_dir = os.getcwd()


        # Verify that the environmental variables 'RGT_MACHINE_NAME', 
        # 'RGT_SCHEDULER_TYPE', and 'RGT_JOBLAUNCHER_TYPE' are defined.
        # Otherwise throw an exception and stop.
        try:
            if rgt_machine_name == None:
                print('No machine name provided. Please set the RGT_MACHINE_NAME variable'.format(rgt_machine_name))
                raise MachineTypeUndefinedEnvironmentalVariableError("RGT_MACHINE_NAME")

            if rgt_scheduler_type == None:
                print('No scheduler type provided. Please set the RGT_SCHEDULER_TYPE variable'.format(rgt_scheduler_type))
                raise MachineTypeUndefinedEnvironmentalVariableError("RGT_SCHEDULER_TYPE")

            if rgt_jobLauncher_type == None:
                print('No scheduler type provided. Please set the RGT_JOBLAUNCHER_TYPE variable'.format(rgt_jobLauncher_type))
                raise MachineTypeUndefinedEnvironmentalVariableError("RGT_JOBLAUNCHER_TYPE")

        except MachineTypeUndefinedEnvironmentalVariableError as my_exception:
            my_exception.what()
            sys.exit()


        message = "Creating machine of type {machine_type} with scheduler of type {scheduler_type} and job launcher of type {job_launcher_type}\n".format(
                                                                                                  machine_type=rgt_machine_name,
                                                                                                  scheduler_type=rgt_scheduler_type,
                                                                                                  job_launcher_type = rgt_jobLauncher_type)
        message += "This machine's starting directory, i.e. path to scripts directory, is '{}'\n".format(rgt_scripts_dir)
        message += "This machine's workspace is '{}'\n".format(rgt_path_to_workspace)
        print(message)

        # We now create a new machine. If the new machine type is not implemented,
        # then warn user, throw an exception and stop.
        tmp_machine = None
        try:
            if rgt_machine_name == "Crest":
                tmp_machine = IBMpower8(name=rgt_machine_name,
                                        scheduler=rgt_scheduler_type,
                                        jobLauncher=rgt_jobLauncher_type,
                                        workspace=rgt_path_to_workspace,
                                        harness_id=rgt_harness_id,
                                        scripts_dir=rgt_scripts_dir)
            elif rgt_machine_name == "Chester":
                tmp_machine = CrayXK7(name=rgt_machine_name,
                                      scheduler=rgt_scheduler_type,
                                      jobLauncher=rgt_jobLauncher_type,
                                      workspace=rgt_path_to_workspace,
                                      harness_id=rgt_harness_id,
                                      scripts_dir=rgt_scripts_dir)
            elif rgt_machine_name == "summitdev":
                tmp_machine = IBMpower8(name=rgt_machine_name,
                                        scheduler=rgt_scheduler_type,
                                        jobLauncher=rgt_jobLauncher_type,
                                        workspace=rgt_path_to_workspace,
                                        harness_id=rgt_harness_id,
                                        scripts_dir=rgt_scripts_dir)
            elif rgt_machine_name == "peak":
                tmp_machine = IBMpower9(name=rgt_machine_name,
                                        scheduler=rgt_scheduler_type,
                                        jobLauncher=rgt_jobLauncher_type,
                                        workspace=rgt_path_to_workspace,
                                        harness_id=rgt_harness_id,
                                        scripts_dir=rgt_scripts_dir)
            elif rgt_machine_name == "summit":
                tmp_machine = IBMpower9(name=rgt_machine_name,
                                        scheduler=rgt_scheduler_type,
                                        jobLauncher=rgt_jobLauncher_type,
                                        workspace=rgt_path_to_workspace,
                                        harness_id=rgt_harness_id,
                                        scripts_dir=rgt_scripts_dir)
            elif rgt_machine_name == "rhea":
                tmp_machine = RHELx86(name=rgt_machine_name,
                                        scheduler=rgt_scheduler_type,
                                        jobLauncher=rgt_jobLauncher_type,
                                        workspace=rgt_path_to_workspace,
                                        harness_id=rgt_harness_id,
                                        scripts_dir=rgt_scripts_dir)
            else:
                print("Machine name does not exist. Good bye!")
                raise MachineTypeNotImplementedError(rgt_machine_name)
        except MachineTypeNotImplementedError as my_exception:
            my_exception.what()
            sys.exit()

        return tmp_machine

