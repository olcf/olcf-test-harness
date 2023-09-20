#!/usr/bin/env python3
"""This module abstracts the application-test input file rgt_test_input.ini.

This modules main responsibilty is to process the file application-test input file.
The input file stores various key-value entries that are parameters for running
the application-test. The extant OLCF Harness currently supports processing input files
of one format: The INI file format.

INI format of application-test input file rgt_test_input.ini
------------------------------------------------------------
The following sections are allowed:

    [Replacements]
    [EnvVars]
    [RuntimeEnvironmentCommands]

The [Replacements] section is the only madatory section. TThe key-value entries
in the section is stored in 2 dictionaries which are attributes of the class 
RgtTest:

    * self.__builtin_params
    * self.__user_params

The method class method self.__is_builtin_param tests if a key-value pair 
belongs in dictionary self.__builtin_params. If a the key-valule fails the test
then the key-value pair is in the dictionary self.__user_params. The key-value pairs
are used for replacements of patterns in template files.  

The [EnvVars] section is optional
The section contains keys-value pairs for setting environmental varibles.

The [RuntimeEnvironmentCommands] section optional. This section contains
key-value entries for where the values ar commands to be run that set the 
runtime environment for each harness task. 
The only permmited keys are 

    * "build_rte_cmd" - key for the command to set the rte for the build task.
    * "submit_rte_cmd" - key for the command to set the rte for the submit task.
    * "check_rte_cmd" - key for the command to set the rte for the check task.
    * "report_rte_cmd" - key for the command to set the rte for the report task.
    * "all_rte_cmd" - key for the command to set the rte for the all tasks.
"""

#
# Author: Veronica G. Vergara L.
#

# Python imports
import configparser
import os
import sys

# Harness imports
from libraries.rgt_utilities import rgt_variable_name_modification
from libraries import rgt_utilities


class RgtTest():
    """This class is the abstraction of regression test input file."""

    RUNTIME_ENVIRONMENT_SECTION_KEYS = {"build" : 'build_rte_cmd',
                                        "submit" : 'submit_rte_cmd',
                                        "check" : 'check_rte_cmd',
                                        "report" : 'report_rte_cmd',
                                        "all"    : 'all_rte_cmd'}
    """Valid key values for the runtime environment section in the rgt_test_input.ini file."""

    HARNESS_SECTION_KEYS = {"application_test_results_dir" : 'results_dir',
                            "application_test_work_dir" : 'working_dir',
                            "application_test_build_dir" : 'build_dir',
                            "application_test_scripts_dir" : 'scripts_dir',
                            "application_test_harness_id" : 'harness_id',
                            "rgt_environmental_file" : "rgtenvironmentalfile",
                            "nccs_test_harness_module_file" : "nccstestharnessmodule" }
    """Valid key values for the Harness parameter dictionary."""


    OBTAIN_FROM_ENVIRONMENT="<obtain_from_environment>"
    """str: The string value for an INI entry that indicates to get the value from the shell environment."""

    def __init__(self, filename,logger=None):
        """ The constructor of the RgtTest class.

        Parameters
        ----------
        filename : str
            The name to the rgt_test.py input file. The input file contains
            test settings, environmental varibles settings and other information
            to run a test/application.
            
        a_logger: A rgt_logger class
            An instance of the rgt_logger class.
        """

        self.__inputfile = filename
        """str: The name to the rgt_test.py application-test input file. """

        self.__logger = logger
        """rgt_logger: An instance of the rgt_logger class."""

        self.__builtin_params = {}
        """dict: The buitin parameters of the application-test input file."""

        self.__user_params = {}
        """dict: A dictionary of the keys and values that are not builtin params.

        These keys and values are found in the "Replacements" section of the
        application-test input file. These key-values are not builtin key-values.
        """

        self.__environ = {}
        """dict: A dictionary of the environmental variables in the application-test input file.

        The dictonary store the keys and values of the EnvVars section of the application-test
        input file.
        """

        self._runtime_environment_params = {}
        """ A dictionary: A dictionary of commands to set the runtime environment.
            
            The keys of the dictionary are strings, and the corrsponding values
            specify a command. See the class variable RUNTIME_ENVIRONMENT_KEYS 
            for valid keys.

            For example, self._runtime_environment_params['build_rte_cmd'] is
            the command to set the runtime environment for building the binary.
         """

        self._harness_params = {}
        """A dictionary: A dictionary of keys and values needed by the harness

            The keys of the dictionary are strings, and the corrsponding values
            are strings. See the class variable HARNESS_KEYS for valid keys.
        """

        # dict of builtin keys - value indicates whether it is required
        self.__builtin_keys = {

            "batch_filename" :     {"required": True, "type": str },
            "batch_queue" :        {"required": False, "type": str },
            "build_cmd" :          {"required": True, "type": str},
            "check_cmd":           {"required": True, "type": str},
            "executable_path" :    {"required": False, "type": str},
            "job_name" :           {"required": True, "type": str},
            "max_submissions" :    {"required": False, "type": int, "valid": lambda x : True if (int(x) >= 1 or int(x) == -1) else False},
            "nodes" :              {"required": True, "type": int, "valid": lambda x: True if (int(x) >= 1) else False},
            "processes_per_node" : {"required": False, "type": int, "valid": lambda x: True if (int(x) >= 1) else False},
            "project_id" :         {"required": False, "type": str},
            "report_cmd" :         {"required": True, "type": str},
            "resubmit" :           {"required": False, "type": int, "valid": lambda x: True if (int(x) == 1 or int(x) == 0) else False},
            "total_processes" :    {"required": False, "type": int, "valid": lambda x: True if (int(x) >= 1) else False},
            "walltime" :           {"required": True, "type": str},
        }

    def __str__(self):
        message =  "\n"
        message += "RgtTest class" + "\n"
        message += "-------------" + "\n"
        message += "Input file name: {}".format(self.test_input_filename) + "\n\n"
        message += "Environmental Variables" + "\n"
        message += "-----------------------" + "\n"
        for (key,value) in self.test_environment.items():
            message += "{} = {}\n".format(key,value)
        message += "\n\n"
        message += "builtin params" + "\n"
        message += "-----------------------" + "\n"
        for (key,value) in self.builtin_parameters.items():
            message += "{} = {}\n".format(key,value)
        message += "\n\n"
        message += "user params" + "\n"
        message += "-----------------------" + "\n"
        for (key,value) in self.user_parameters.items():
            message += "{} = {}\n".format(key,value)
        message += "harness params" + "\n"
        message += "-----------------------" + "\n"
        for (key,value) in self.harness_parameters.items():
            message += "{} = {}\n".format(key,value)
        message += "\n\n"

        
        return message

    @property
    def test_input_filename(self):
        """str: Returns the application-test input filename."""
        return self.__inputfile

    #
    # Methods to manage user parameters and environment
    #
    @property
    def user_parameters(self):
        """dict: The dictionary user parameters of the application-test input file."""
        return self.__user_params
    #
    # Methods to manage builtin parameters
    #

    @property
    def builtin_parameters(self):
        """dict: The dictionary of builtin parameters of the application-test input file."""
        return self.__builtin_params

    def print_user_parameters(self):
        print("RGT Test Parameters - User")
        print("==========================")
        for (k,v) in (self.user_parameters).items():
            print(k,"=",v)

    # Methods to manage runtime environment commands
    @property
    def runtime_environment_params(self):
        """dict: The dictionary of key-values for setting the runtime environment commands."""
        return self._runtime_environment_params

    @runtime_environment_params.setter
    def runtime_environment_params(self,params):
        """Sets the commands for the setting various runtime environment commands.

        Parameters
        ----------
        params
            A dictionary where the keys and values are strings.
        """
        for (key,val) in params.items():
            if key in self.RUNTIME_ENVIRONMENT_SECTION_KEYS.values():
                self._runtime_environment_params[key] = val
            else:
                # To do is throw an exception if an invalid key,value is assigned.
                pass

    @property
    def build_runtime_environment_command_file(self):
        """str: The command file to set the runtime environment for building the binary."""
        key = self.RUNTIME_ENVIRONMENT_SECTION_KEYS["build"]
        command = self._get_rte_param(key)
        return command

    @property
    def submit_runtime_environment_command_file(self):
        """str: The command file to set the runtime environment for submitting the batch script."""
        key = self.RUNTIME_ENVIRONMENT_SECTION_KEYS["submit"]
        command = self._get_rte_param(key)
        return command

    @property
    def check_runtime_environment_command_file(self):
        """str: The command file to set the runtime environment for checking the test results."""
        key = self.RUNTIME_ENVIRONMENT_SECTION_KEYS["check"]
        command = self._get_rte_param(key)
        return command

    @property
    def report_runtime_environment_command_file(self):
        """str: The command file to set the runtime environment for reporting the test results."""
        key = self.RUNTIME_ENVIRONMENT_SECTION_KEYS["report"]
        command = self._get_rte_param(key)
        return command

    #
    # Methods to retrieve full test dictionaries
    #

    @property
    def test_environment(self):
        """dict: Returns a dictionary of the application-test environmental variables."""
        return self.__environ

    @test_environment.setter
    def test_environment(self, envvars_view):
        self.__environ.update(envvars_view)

    @property
    def test_parameters(self):
        """dict: Returns a dictionary of all key-values in the application-test input file."""
        parameters = self.builtin_parameters
        parameters.update(self.user_parameters)
        parameters.update(self.runtime_environment_params)
        return parameters

    @test_parameters.setter
    def test_parameters(self,params):
        """Updates the appropiate test parameter dictionary.

        This method is fragile. Suppose there is builtin and
        user parameter that has the same key, then only one 1
        dictionary gets updated. What we really need to know is the
        section and the key-value to update the appropiate dictionaries.
        """
        for (k,v) in params.items():
            if self._is_builtin_param(k):
                self._set_builtin_param(k, v)
            else:
                self._set_user_param(k, v)

    @property
    def harness_parameters(self):
        """Returns a dictionary of the harness test parameters

        Returns
        -------
        dict:
            The dictionary will have the key values found in 
            HARNESS_SECTION_KEYS.values(), HARNESS_SECTION_KEYS is 
            a dictionary.
        """
        return self._harness_params

    @harness_parameters.setter
    def harness_parameters(self,params):
        """Updates the harness parameter dictionary.

        Parameters
        ----------
        params : dict
            A dictionary of the harness parameters. The keys and values
            are strings.
        """
        for (key,value) in params.items():
            if key in self.HARNESS_SECTION_KEYS.values():
                self._harness_params[key] = value 
            else:
                # TODO: Throw an exception if an invalid key,value is assigned.
                print("No key found for", key)

    def get_test_replacements(self):
        """Returns a dictionary of key word replacements.

        In the application-test input file there are entries in the replacement
        of the form key1 = value1. Correspondingly, there are records in the template
        files with __key1__. The returned dictionary contains {...,  __key1__ : value1, ...}
        and is used to make the appropiate substitutions in the templates file to form the
        correct files.

        Returns
        -------
            dict:
                Returns a dictionary with entries of form
                { ..., "__key1__" : value1, ...} where key1 is a replacement
                key found in the Replacements section of application-test input file
                rgt_test_input.ini.
        """
        replacements = {}
        for (k,v) in (self.builtin_parameters).items():
            replace_key = '__' + k + '__'
            replacements[replace_key] = v

        for (k,v) in (self.user_parameters).items():
            replace_key = '__' + k + '__'
            replacements[replace_key] = v

        for (k,v) in (self.harness_parameters).items():
            replace_key = '__' + k + '__'
            replacements[replace_key] = v

        return replacements

    #
    # Convenience methods for setting specific parameters
    #
    def set_launch_id(self, value):
        self._set_builtin_param("launch_id", value)

    def set_max_submissions(self, value):
        self._set_builtin_param("max_submissions", value)

    #
    # Convenience methods for retrieving specific parameters
    #

    def get_batch_file(self):
        return self._get_builtin_param("batch_filename")

    def get_batch_queue(self):
        return self._get_builtin_param("batch_queue")

    def get_build_command(self):
        return self._get_builtin_param("build_cmd")

    def get_check_command(self):
        return self._get_builtin_param("check_cmd")

    def get_report_command(self):
        return self._get_builtin_param("report_cmd")

    def get_executable(self):
        return self._get_builtin_param("executable_path")

    def get_jobname(self):
        return self._get_builtin_param("job_name")

    def get_launch_id(self):
        return self._get_builtin_param("launch_id")

    def get_max_submissions(self):
        return self._get_builtin_param("max_submissions")

    def get_nodes(self):
        return self._get_builtin_param("nodes")

    def get_project(self):
        return self._get_builtin_param("project_id")

    def get_walltime(self):
        return self._get_builtin_param("walltime")

    def get_total_processes(self):
        val = self._get_builtin_param("total_processes")
        if not val:
            return str(0)
        else:
            return val

    def get_processes_per_node(self):
        val = self._get_builtin_param("processes_per_node")
        if not val:
            return str(0)
        else:
            return val

    #
    # Input file readers
    #

    def read_input_file(self):
        """Processes the appliction-test input file.

        The functions exits if the application-test input filename 
        is not a permitted value.
        """
        try:
            if os.path.isfile(self.test_input_filename):
                self._read_rgt_input_ini()
                self._reconcile_with_shell_environment_variables()
                self._check_parameters()
                self._print_test_parameters()
            else:
                error_message = "Test input file {} not found".format(self.test_input_filename)
                raise ErrorRgtTestInputFileNotFound(error_message)
        except ErrorRgtParameterReconcile as err:
            self.__logger.doCriticalLogging(err.message)
            sys.exit(err.message)
        except ErrorRgtTestInputFileNotFound as err:
            self.__logger.doCriticalLogging(err.message)
            sys.exit(err.message)

    # Private methods

    def _set_builtin_param(self, key, value):
        self.builtin_parameters[key] = value

    def _get_builtin_param(self, key):
        if key in self.builtin_parameters:
            return (self.builtin_parameters)[key]
        else:
            return None

    def _is_builtin_param(self, key):
        return key in self.__builtin_keys

    def _get_rte_param(self,key):
        command = ""
        if key in self.runtime_environment_params:
            command = self.runtime_environment_params[key]
        return command

    def _set_builtin_param(self, key, val, warn=True):
        if self._is_builtin_param(key):
            self.__builtin_params[key] = val
            return True
        else:
            if warn:
                print("WARNING: Ignoring invalid built-in parameter key {}".format(key))
            return False

    def _is_rte_param(self,key):
        return key in self.RUNTIME_ENVIRONMENT_SECTION_KEYS.values()

    def _update_replacement_parameters(self,params_view):
        """Updates the appropiate replacement parameter dictionary as required."""
        for (k,v) in params_view:
            if self._is_builtin_param(k):
                self._set_builtin_param(k, v)
            else:
                self._set_user_param(k, v)

    def _read_rgt_input_ini(self):
        rgt_test_config = configparser.ConfigParser()
        rgt_test_config.read(self.test_input_filename)

        if not 'Replacements' in rgt_test_config:
            print("ERROR: missing [Replacements] section in test input")
            replace = dict()
        else:
            replace = rgt_test_config['Replacements']
        self._update_replacement_parameters(replace.items())

        # Update environment if either batch_queue or project_id is set
        env_dict = {}
        bq = self.get_batch_queue()
        if bq:
            env_dict['batch_queue'] = bq
        proj = self.get_project()
        if proj:
            env_dict['project_id'] = proj
        rgt_utilities.set_harness_environment(env_dict, override=True)

        if 'EnvVars' in rgt_test_config:
            env_vars = rgt_test_config['EnvVars']
            self.test_environment = env_vars

        # We now extract the runtime environment commands.
        rte_section = 'RuntimeEnvironmentCommands'
        if rte_section in rgt_test_config:
            runtime_env_commands = rgt_test_config[rte_section]
        else:
            runtime_env_commands = dict() 
        self.runtime_environment_params = runtime_env_commands 

    def _print_test_parameters(self):
        self._print_builtin_parameters()
        self.print_user_parameters()
    
    def _reconcile_with_shell_environment_variables(self):
        # Reconcile the builtin parameters, self.__builtin_params, with the
        # shell environment variables.
        for (key,value) in self.__builtin_params.items():
            if value == self.OBTAIN_FROM_ENVIRONMENT:
                key_modified = rgt_variable_name_modification(key)
                tmp_value = os.getenv(key_modified)
                if tmp_value :
                    self.__builtin_params[key] = tmp_value
                else :
                    error_message = "Unable to reconcile shell environmental variables and self.__builtin_params[{key}]={value}.".format(key=key,value=value)
                    raise ErrorRgtParameterReconcile(error_message)

        # Reconcile the user parameters, self.__user_params, with
        # the shell environment variables.
        for (key,value) in self.__user_params.items():
            if value == self.OBTAIN_FROM_ENVIRONMENT:
                key_modified = rgt_variable_name_modification(key)
                tmp_value = os.getenv(key_modified)
                if tmp_value :
                    self.__builtin_params[key] = tmp_value
                else :
                    error_message = "Unable to reconcile shell environmental variables and self.__user_params[{key}]={value}.".format(key=key,value=value)
                    raise ErrorRgtParameterReconcile(error_message)


        # Reconcile the environment parameters, self.__environ, with
        # the shell environment variables.
        for (key,value) in self.__environ.items():
            if value == self.OBTAIN_FROM_ENVIRONMENT:
                key_modified = rgt_variable_name_modification(key)
                tmp_value = os.getenv(key_modified)
                if tmp_value :
                    self.__environ[key] = tmp_value
                else :
                    error_message = "Unable to reconcile shell environmental variables and self.__environ[{key}]={value}.".format(key=key,value=value)
                    raise ErrorRgtParameterReconcile(error_message)
        return

    def _check_parameters(self):
        # Check validation parameters for input
        # Start with the required flag
        error_message = ""
        for (k,params) in self.__builtin_keys.items():
            if 'required' in params and params['required'] and k not in self.builtin_parameters:
                error_message += "ERROR: required test input parameter {} is not set!\n".format(k)

        # Check type
        for (k,params) in self.__builtin_keys.items():
            valid_type = True
            if 'type' in params and k in self.builtin_parameters:
                # All params are strings, so no need to test that
                # Check int
                if params['type'] is int and not self.builtin_parameters[k].lstrip("-").isdigit():
                    valid_type = False # Need to reference in lambda function
                    error_message += "ERROR: test input parameter {} is not type {}!\n".format(k, str(params['type']))

                # Check file
                if params['type'] == 'file':
                    # Check whether it exists
                    if not os.path.exists(self.builtin_parameters[k]):
                        error_message += "ERROR: test input parameter {} does not exist {}!\n".format(k, self.builtin_parameters[k])

                    # Check whether is executable
                    if not os.access(self.builtin_parameters[k], os.X_OK):
                        error_message += "ERROR: test input parameter {} is not executable {}!\n".format(k, self.builtin_parameters[k])

            if 'valid' in params and k in self.builtin_parameters:
                # Run our validation function
                if valid_type == False or not params['valid'](self.builtin_parameters[k]):
                    error_message += "ERROR: test input parameter {} failed validation!\n".format(k)


        # Print and bail if any errors
        if error_message != "":
            self.__logger.doCriticalLogging(error_message)
            exit(1)

    def _print_builtin_parameters(self):
        print("RGT Test Parameters - Builtin")
        print("=============================")
        for (k,v) in (self.builtin_parameters).items():
            print(k,"=",v)

    def _set_user_param(self, key, val):
        self.__user_params[key] = val


class RgtTestError(Exception):
    """Base error class for RgtTest."""
    def __init__(self,message):
        """The class constructor

        Parameters
        ----------
        message : string
            The error message for this exception.
        """
        self._message = message
        return
    
    @property
    def message(self):
        """str: The error message."""
        return self._message
    
class ErrorRgtParameterReconcile(RgtTestError):
    """Exception raised for errors in reconciling RgtTest parameters."""
    def __init__(self,message):
        RgtTestError.__init__(self,message)
        return

class ErrorRgtTestInputFileNotFound(RgtTestError):
    """Exception raised for errors when the rgt_test_input.ini is not found."""
    def __init__(self,message):
        RgtTestError.__init__(self,message)
        return

if __name__ == "__main__":
    print('This is the RgtTest class')
