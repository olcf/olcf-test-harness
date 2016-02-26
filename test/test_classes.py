from cray_xk7 import CrayXK7 
from machine_factory import MachineFactory

#my_machine = CrayXK7('Chester','LSF')
#print my_machine.get_machine_name()
#my_machine.print_scheduler_info()

fc = MachineFactory.create_machine('Chester','XK7','PBS')
