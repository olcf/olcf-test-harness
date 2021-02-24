class MachineTypeError(Exception):
    """Base class for exceptions in this module."""
    pass

class MachineTypeNotImplementedError(MachineTypeError):
    """Machine type is not implemented"""
    def __init__(self,
                 machine_type):
        self.machine_type = machine_type
        return
    
    def what(self):
        message = "The machine type '{}' is not implemented.".format(self.machine_type)
        print(message)
    
class MachineTypeUndefinedVariableError(MachineTypeError):
    """A machine configuration variable is undefined"""
    def __init__(self,
                 cfg_variable):
        self.cfg_variable = cfg_variable
        return

    def what(self):
        message = "The machine configuration variable '{}' is undefined.".format(self.cfg_variable)
        print(message)
