import os
from cray_xk7 import CrayXK7
from ibm_power8 import IBMpower8


class MachineFactory:

    @staticmethod
    def create_machine():
        rgt_machine_name = os.environ["RGT_MACHINE_NAME"]
        rgt_scheduler_type = os.environ["RGT_SCHEDULER_TYPE"]
        print("Creating machine "+str(rgt_machine_name)+" with scheduler "+str(rgt_scheduler_type))

        tmp_machine = None
        if rgt_machine_name == "Crest":
            tmp_machine = IBMpower8(name=rgt_machine_name,scheduler=rgt_scheduler_type)
        else:
            print("Machine name does not exit. Good bye!")

        return tmp_machine

    def __init__(self):
        pass

