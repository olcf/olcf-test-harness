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

"""

#
# Author: Veronica G. Vergara L.
#

# Python imports
import configparser
import os
import sys
from pathlib import Path
try:
    # YAML & Jinja2 must be used together
    import yaml
    from jinja2 import Template
    yaml_disabled = False
except ModuleNotFoundError:
    yaml_disabled = True

# Harness imports
from libraries.rgt_utilities import rgt_variable_name_modification
from libraries import rgt_utilities

class RgtTest():
    """This class is the abstraction of regression test input file."""

    HARNESS_SECTION_KEYS = {"application_test_results_dir" : 'results_dir',
                            "application_test_work_dir" : 'working_dir',
                            "application_test_build_dir" : 'build_dir',
                            "application_test_scripts_dir" : 'scripts_dir',
                            "application_test_harness_id" : 'harness_id'}
    """Valid key values for the Harness parameter dictionary."""


    OBTAIN_FROM_ENVIRONMENT="<obtain_from_environment>"
    """str: The string value for an entry that indicates to get the value from the shell environment."""

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
            "job_name" :           {"required": True, "type": str},
            "max_submissions" :    {"required": False, "type": int, "valid": lambda x : True if (int(x) >= 1 or int(x) == -1) else False},
            "nodes" :              {"required": True, "type": int, "valid": lambda x: True if (int(x) >= 1) else False},
            "project_id" :         {"required": False, "type": str},
            "report_cmd" :         {"required": True, "type": str},
            "resubmit" :           {"required": False, "type": int, "valid": lambda x: True if (int(x) == 1 or int(x) == 0) else False},
            "use_batch_template":  {"required": False, "type": int, "valid": lambda x: True if (int(x) == 1 or int(x) == 0) else False}
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
        self.__logger.doInfoLogging("RGT Test Parameters - User")
        self.__logger.doInfoLogging("==========================")
        for (k,v) in (self.user_parameters).items():
            self.__logger.doInfoLogging(f'{k}={v}')

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
                self.__logger.doCriticalLogging("No key found for", key)

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
        def name_mangle(yaml_origin, name):
            return name if yaml_origin else f'__{name}__'

        replacements = {}
        is_yaml = self.__inputfile.endswith('yaml')
        for (k,v) in (self.builtin_parameters).items():
            replacements[name_mangle(is_yaml, k)] = v

        for (k,v) in (self.user_parameters).items():
            replacements[name_mangle(is_yaml, k)] = v

        for (k,v) in (self.harness_parameters).items():
            replacements[name_mangle(is_yaml, k)] = v

        return replacements

    #
    # Convenience methods for setting specific parameters
    #
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

    def get_jobname(self):
        return self._get_builtin_param("job_name")

    def get_max_submissions(self):
        return self._get_builtin_param("max_submissions")

    def get_use_batch_template(self):
        return self._get_builtin_param("use_batch_template")

    def get_nodes(self):
        return self._get_builtin_param("nodes")

    def get_project(self):
        return self._get_builtin_param("project_id")

    #
    # Input file readers
    #

    def read_input_file(self):
        """Processes the appliction-test input file.

        The functions exits if the application-test input filename 
        is not a permitted value.
        """
        try:
            if Path(self.test_input_filename).is_file():
                if self.test_input_filename.endswith('ini'):
                    self._read_rgt_input_ini()
                elif self.test_input_filename.endswith('yaml'):
                    if yaml_disabled:
                        self.__logger.doCriticalLogging("import yaml failed, YAML test input file cannot be loaded. Please pip install pyyaml in the current Python environment.")
                        exit(1)
                    self._read_rgt_input_yaml()
                else:
                    error_message = "File type of input file {} not supported (expected yaml or ini).".format(self.test_input_filename)
                    raise ErrorRgtTestInputFileNotFound(error_message)
                self._reconcile_with_shell_environment_variables()
                self._check_parameters()
                self._print_test_parameters()
            else:
                error_message = "Test input file {} not found".format(self.test_input_filename)
                raise ErrorRgtTestInputFileNotFound(error_message)
        except Exception as err:
            self.__logger.doCriticalLogging(err.message)
            exit(1)

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

    def _set_builtin_param(self, key, val, warn=True):
        if self._is_builtin_param(key):
            self.__builtin_params[key] = val
            return True
        else:
            if warn:
                self.__logger.doWarningLogging("WARNING: Ignoring invalid built-in parameter key {}".format(key))
            return False

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
            raise Exception("Missing [Replacements] section in test input")
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

    def _read_rgt_input_yaml(self):
        with open(self.test_input_filename, 'r') as file:
            test_yaml_raw = yaml.safe_load(file)

        # Catch a few fatal errors and throw exceptions if encountered
        if not 'replacements' in test_yaml_raw.keys():
            raise Exception("Missing Replacements section in YAML test input")
        elif 'variables' in test_yaml_raw.keys() and not isinstance(test_yaml_raw["variables"], dict):
            # variables must be a single key-value dict, not a list of dicts
            raise Exception("Variables are provided in the YAML test input, but is not a dictionary")

        if 'variables' in test_yaml_raw.keys():
            # then do string formatting only for string data types
            rgt_test_config = { k: v.format(**test_yaml_raw["variables"]) if isinstance(v, str) else v 
                                    for k, v in test_yaml_raw["replacements"].items() }
        else:
            # then no variable usage, just copy replacements block to test config
            rgt_test_config = test_yaml_raw["replacements"]

        self._update_replacement_parameters(rgt_test_config.items())

        # Update environment if either batch_queue or project_id is set
        env_dict = {}
        bq = self.get_batch_queue()
        if bq:
            env_dict['batch_queue'] = bq
        proj = self.get_project()
        if proj:
            env_dict['project_id'] = proj
        rgt_utilities.set_harness_environment(env_dict, override=True)

        # EnvVars and RuntimeEnvironmentParams are not supported in YAML format
        self.test_environment = dict()
        self.runtime_environment_params = dict()

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
                    self.__user_params[key] = tmp_value
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
                if params['type'] is int and not (isinstance(self.builtin_parameters[k],int) or \
                        self.builtin_parameters[k].lstrip("-").isdigit()):
                    valid_type = False # Need to reference in lambda function
                    error_message += "ERROR: test input parameter {} is not type {}!\n".format(k, str(params['type']))

                # Check file
                if params['type'] == 'file':
                    # Check whether it exists
                    if not Path(self.builtin_parameters[k]).exists():
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
        self.__logger.doInfoLogging("RGT Test Parameters - Builtin")
        self.__logger.doInfoLogging("=============================")
        for (k,v) in (self.builtin_parameters).items():
            self.__logger.doInfoLogging(f'{k}={v}')

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
