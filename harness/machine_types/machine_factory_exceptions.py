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
    
class MachineTypeUndefinedEnvironmentalVariableError(MachineTypeError):
    """An environmental variable is undefined"""
    def __init__(self,
                 env_variable):
        self.env_variable = env_variable
        return

    def what(self):
        message = "The environmental varaible '{}' is undefined.".format(self.env_variable)
        print(message)
