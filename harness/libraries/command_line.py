#! /usr/bin/env python3
## @module command_line
#  This module contains utility classes, functions, etc for command line management.
#

# System imports

# Local imports

# A class that will store the parsed command line arguments.
class HarnessParsedArguments:
    def __init__(self, inputfile=None,
                       loglevel=None,
                       configfile=None,
                       runmode=None,
                       stdout_stderr=None,
                       use_fireworks=False,
                       separate_build_stdio=False):

        self.__inputfile = inputfile
        self.__loglevel = loglevel
        self.__configfile = configfile
        self.__mode = runmode
        self.__stdout_stderr = stdout_stderr
        self.__use_fireworks = use_fireworks
        self.__separate_build_stdio = separate_build_stdio

        self.__verify_attributes()

    def __verify_attributes(self):
         for attr, value in self.__dict__.items():
             if value == None:
                 message="The class HarnessParsedArguments instantiated incorrectly!\n"
                 message+="The class HarnessParsedArguments must be instantiated with\n"
                 message+="all keyword arguments having non-None values."
                 message+="Key:{attr}; value:{value}\n".format(attr=attr,value=value)
                 raise HPA_AttributeError(message)
                
    @property
    def inputfile(self):
        return self.__inputfile

    @property
    def loglevel(self):
        return self.__loglevel

    @property
    def configfile(self):
        return self.__configfile

    @property
    def runmode(self):
        return self.__mode

    @property
    def stdout_stderr(self):
        return self.__stdout_stderr

    @stdout_stderr.setter
    def stdout_stderr(self,value):
        self.__stdout_stderr = value

    @property
    def use_fireworks(self):
        return self.__use_fireworks

    @property
    def separate_build_stdio(self):
        return self.__separate_build_stdio

    @property
    def effective_command_line(self):
        command_options = ("Effective command line: "
                           "runtests.py"
                           " --inputfile {my_inputfile}"
                           " --configfile {my_configfile}"
                           " --loglevel {my_loglevel}"
                           " --output {my_output}"
                           " --separate-build-stdio"
                           " --mode {my_runmode}")

        run_mode_args=" ".join(self.runmode) 

        efc = command_options.format(my_inputfile = self.inputfile,
                                     my_configfile = self.configfile,
                                     my_loglevel = self.loglevel,
                                     my_output = self.stdout_stderr,
                                     my_runmode = run_mode_args)

        return efc


class BaseError(Exception):
    pass

class HPA_AttributeError(BaseError):
    def __init__(self,message=None):
        self.message = message

def main():
    pass

if __name__ == "__main__":
    main()
