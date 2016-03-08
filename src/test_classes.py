from cray_xk7 import CrayXK7 
from ibm_power8 import IBMpower8
from machine_factory import MachineFactory
from lsf import LSF

my_machine = CrayXK7('Chester','PBS')
print my_machine.get_machine_name()
my_machine.print_scheduler_info()

my_machine = IBMpower8('Crest','LSF')
print my_machine.get_machine_name()
my_machine.print_scheduler_info()

fc = MachineFactory.create_machine('Chester','XK7','PBS')
fc = MachineFactory.create_machine('Crest','Power8','LSF')

my_scheduler = LSF('LSF','poe')
print my_scheduler.get_scheduler_name()
