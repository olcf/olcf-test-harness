"""
This module implements the application-test input file, rgt_test_input.{ini,yaml}.
"""

from __future__ import annotations

import configparser
import os
from pathlib import Path
from typing import ClassVar

try:
    import yaml

    yaml_disabled = False
except ModuleNotFoundError:
    yaml_disabled = True

# Harness imports
from oth.libraries import rgt_utilities
from oth.libraries.rgt_utilities import oth_variable_name_modification


class RgtTest:
    """This class is the abstraction of regression test input file."""

    HARNESS_SECTION_KEYS: ClassVar[dict[str, str]] = {
        "application_test_results_dir": "results_dir",
        "application_test_work_dir": "working_dir",
        "application_test_build_dir": "build_dir",
        "application_test_scripts_dir": "scripts_dir",
        "application_test_harness_id": "harness_id",
    }
    """Valid key values for the Harness parameter dictionary."""

    OBTAIN_FROM_ENVIRONMENT = "<obtain_from_environment>"
    """str: The string value for an entry that indicates to get the value from the shell environment."""

    def __init__(self, filename: str):
        """The constructor of the RgtTest class.

        Parameters
        ----------
        filename : str
            The name to the rgt_test.py input file. The input file contains
            test settings, environmental varibles settings and other information
            to run a test/application.
        """

        self.__inputfile = filename

        self.__builtin_params: dict[str, str] = {}
        """dict: The buitin parameters of the application-test input file."""

        self.__user_params: dict[str, str] = {}
        """dict: A dictionary of the keys and values that are not builtin params.

        These keys and values are found in the "Replacements" section of the
        application-test input file. These key-values are not builtin key-values.
        """

        self.__environ: dict[str, str] = {}
        """dict: A dictionary of the environmental variables in the application-test input file.

        The dictonary store the keys and values of the EnvVars section of the application-test
        input file.
        """

        self._harness_params: dict[str, str] = {}
        """A dictionary: A dictionary of keys and values needed by the harness

            The keys of the dictionary are strings, and the corrsponding values
            are strings. See the class variable HARNESS_KEYS for valid keys.
        """

        # dict of builtin keys - value indicates whether it is required
        self.__builtin_keys = {
            "batch_filename": {"required": True, "type": str},
            "batch_queue": {"required": False, "type": str},
            "build_cmd": {"required": True, "type": str},
            "check_cmd": {"required": True, "type": str},
            "job_name": {"required": True, "type": str},
            "max_submissions": {
                "required": False,
                "type": int,
                "valid": lambda x: bool(int(x) >= 1 or int(x) == -1),
            },
            "nodes": {
                "required": True,
                "type": int,
                "valid": lambda x: bool(int(x) >= 1),
            },
            "project_id": {"required": False, "type": str},
            "report_cmd": {"required": False, "type": str},
            "use_batch_template": {
                "required": False,
                "type": int,
                "valid": lambda x: bool(int(x) == 1 or int(x) == 0),
            },
            "run_local": {
                "required": False,
                "type": int,
                "valid": lambda x: bool(int(x) == 1 or int(x) == 0),
            },
        }

    def __str__(self):
        message = "\n"
        message += "RgtTest class" + "\n"
        message += "-------------" + "\n"
        message += f"Input file name: {self.test_input_filename}\n\n"
        message += "Environmental Variables" + "\n"
        message += "-----------------------" + "\n"
        for key, value in self.test_environment.items():
            message += f"{key} = {value}\n"
        message += "\n\n"
        message += "builtin params" + "\n"
        message += "-----------------------" + "\n"
        for key, value in self.builtin_parameters.items():
            message += f"{key} = {value}\n"
        message += "\n\n"
        message += "user params" + "\n"
        message += "-----------------------" + "\n"
        for key, value in self.user_parameters.items():
            message += f"{key} = {value}\n"
        message += "harness params" + "\n"
        message += "-----------------------" + "\n"
        for key, value in self.harness_parameters.items():
            message += f"{key} = {value}\n"
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
    def test_parameters(self, params):
        """Updates the appropiate test parameter dictionary.

        This method is fragile. Suppose there is builtin and
        user parameter that has the same key, then only one 1
        dictionary gets updated. What we really need to know is the
        section and the key-value to update the appropiate dictionaries.
        """
        for k, v in params.items():
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
    def harness_parameters(self, params):
        """Updates the harness parameter dictionary.

        Parameters
        ----------
        params : dict
            A dictionary of the harness parameters. The keys and values
            are strings.
        """
        for key, value in params.items():
            if key in self.HARNESS_SECTION_KEYS.values():
                self._harness_params[key] = value
            else:
                raise ValueError(f"Attempted to set invalid key: {key}")

    def get_test_replacements(self):
        """Returns a dictionary of key-value replacements from the test input file.

        Returns
        -------
            dict:
                Returns a dictionary with entries of form
                { ..., "__key1__" : value1, ...} where key1 is a replacement
                key found in the Replacements section of application-test input file
                rgt_test_input.ini.
        """

        def name_mangle(yaml_origin, name):
            return name if yaml_origin else f"__{name}__"

        replacements = {}
        is_yaml = self.__inputfile.endswith("yaml")
        for k, v in (self.builtin_parameters).items():
            replacements[name_mangle(is_yaml, k)] = v

        for k, v in (self.user_parameters).items():
            replacements[name_mangle(is_yaml, k)] = v

        for k, v in (self.harness_parameters).items():
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

    def get_run_local(self):
        return self._get_builtin_param("run_local")

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
        if Path(self.test_input_filename).is_file():
            if self.test_input_filename.endswith("ini"):
                self._read_rgt_input_ini()
            elif self.test_input_filename.endswith("yaml"):
                if yaml_disabled:
                    raise ImportError(
                        "import yaml failed, YAML test input file cannot be loaded. Please install pyyaml in the current Python environment."
                    )
                self._read_rgt_input_yaml()
            else:
                error_message = f"File type of input file {self.test_input_filename} not supported (expected yaml or ini)."
                raise ValueError(error_message)
            self._reconcile_with_shell_environment_variables()
            self._check_parameters()
        else:
            raise FileNotFoundError(
                f"Test input file not found: {self.test_input_filename}"
            )

    def print_test_parameters(self, logger):
        self._print_builtin_parameters(logger)
        self._print_user_parameters(logger)

    # Private methods

    def _get_builtin_param(self, key):
        if key in self.builtin_parameters:
            return (self.builtin_parameters)[key]
        else:
            return None

    def _is_builtin_param(self, key):
        return key in self.__builtin_keys

    def _set_builtin_param(self, key, val):
        if self._is_builtin_param(key):
            self.__builtin_params[key] = val
            return True
        else:
            raise ValueError(f"Attempted to set invalid built-in parameter key: {key}")

    def _update_replacement_parameters(self, params_view):
        """Updates the appropiate replacement parameter dictionary as required."""
        for k, v in params_view:
            if self._is_builtin_param(k):
                self._set_builtin_param(k, v)
            else:
                self._set_user_param(k, v)

    def _read_rgt_input_ini(self):
        rgt_test_config = configparser.ConfigParser()
        rgt_test_config.read(self.test_input_filename)

        if not "Replacements" in rgt_test_config:
            raise ValueError("Missing [Replacements] section in test input")
        else:
            replace = rgt_test_config["Replacements"]
        self._update_replacement_parameters(replace.items())

        # Update environment if either batch_queue or project_id is set
        env_dict = {}
        bq = self.get_batch_queue()
        if bq:
            env_dict["batch_queue"] = bq
        proj = self.get_project()
        if proj:
            env_dict["project_id"] = proj
        rgt_utilities.set_harness_environment(env_dict, override=True)

        if "EnvVars" in rgt_test_config:
            env_vars = rgt_test_config["EnvVars"]
            self.test_environment = env_vars

    def _read_rgt_input_yaml(self):
        with open(self.test_input_filename, "r") as file:
            test_yaml_raw = yaml.safe_load(file)

        # Catch a few fatal errors and throw exceptions if encountered
        if not "replacements" in test_yaml_raw:
            raise ValueError("Missing Replacements section in YAML test input")
        elif "variables" in test_yaml_raw and not isinstance(
            test_yaml_raw["variables"], dict
        ):
            # variables must be a single key-value dict, not a list of dicts
            raise ValueError(
                "Variables are provided in the YAML test input, but is not a dictionary"
            )

        if "variables" in test_yaml_raw:
            # then do string formatting only for string data types
            rgt_test_config = {
                k: v.format(**test_yaml_raw["variables"]) if isinstance(v, str) else v
                for k, v in test_yaml_raw["replacements"].items()
            }
        else:
            # then no variable usage, just copy replacements block to test config
            rgt_test_config = test_yaml_raw["replacements"]

        self._update_replacement_parameters(rgt_test_config.items())

        # Update environment if either batch_queue or project_id is set
        env_dict = {}
        bq = self.get_batch_queue()
        if bq:
            env_dict["batch_queue"] = bq
        proj = self.get_project()
        if proj:
            env_dict["project_id"] = proj
        rgt_utilities.set_harness_environment(env_dict, override=True)

        # EnvVars and RuntimeEnvironmentParams are not supported in YAML format
        self.test_environment = {}
        self.runtime_environment_params = {}

    def _reconcile_with_shell_environment_variables(self):
        # Resolve any <obtain_from_environment> variables
        for key, value in self.__builtin_params.items():
            if value == self.OBTAIN_FROM_ENVIRONMENT:
                key_modified = oth_variable_name_modification(key)
                tmp_value = os.getenv(key_modified)
                if tmp_value:
                    self.__builtin_params[key] = tmp_value
                else:
                    error_message = f"Unable to find environment variable to fulfill self.__builtin_params[{key}]={value}."
                    raise ValueError(error_message)

        # Reconcile the user parameters, self.__user_params, with
        # the shell environment variables.
        for key, value in self.__user_params.items():
            if value == self.OBTAIN_FROM_ENVIRONMENT:
                key_modified = oth_variable_name_modification(key)
                tmp_value = os.getenv(key_modified)
                if tmp_value:
                    self.__user_params[key] = tmp_value
                else:
                    error_message = f"Unable to find environment variable to fulfill self.__user_params[{key}]={value}."
                    raise ValueError(error_message)

        # Reconcile the environment parameters, self.__environ, with
        # the shell environment variables.
        for key, value in self.__environ.items():
            if value == self.OBTAIN_FROM_ENVIRONMENT:
                key_modified = oth_variable_name_modification(key)
                tmp_value = os.getenv(key_modified)
                if tmp_value:
                    self.__environ[key] = tmp_value
                else:
                    error_message = f"Unable to reconcile shell environmental variables and self.__environ[{key}]={value}."
                    raise ValueError(error_message)

    def _check_parameters(self):
        # Check validation parameters for input
        # Start with the required flag
        errs = []
        for k, params in self.__builtin_keys.items():
            if (
                "required" in params
                and params["required"]
                and k not in self.builtin_parameters
            ):
                errs.append(f"\tRequired test input parameter {k} is not set!")

        # Check type
        for k, params in self.__builtin_keys.items():
            valid_type = True
            if "type" in params and k in self.builtin_parameters:
                # All params are strings, so no need to test that
                # Check int
                if params["type"] is int and not (
                    isinstance(self.builtin_parameters[k], int)
                    or self.builtin_parameters[k].lstrip("-").isdigit()
                ):
                    valid_type = False  # Need to reference in lambda function
                    errs.append(
                        f"\tTest input parameter {k} is not type {params['type']!s}!"
                    )

                # Check file
                if params["type"] == "file":
                    # Check whether it exists
                    if not Path(self.builtin_parameters[k]).exists():
                        errs.append(
                            "\tTest input parameter {k} is expected to be a file, but does not exist:{self.builtin_parameters[k]}!"
                        )

                    # Check whether is executable
                    if not os.access(self.builtin_parameters[k], os.X_OK):
                        errs.append(
                            f"\tTest input parameter {k} is not executable: {self.builtin_parameters[k]}!"
                        )

            if ("valid" in params and k in self.builtin_parameters) and (
                valid_type == False or not params["valid"](self.builtin_parameters[k])
            ):
                errs.append(f"\tTest input parameter {k} failed validation!")

        # Print and bail if any errors
        if len(errs) > 0:
            err_msg = "Test parameter validation failed due to the following errors:\n"
            err_msg += "\n".join(errs)
            raise ValueError(err_msg)

    def _print_user_parameters(self, logger):
        logger.log_info("RGT Test Parameters - User")
        logger.log_info("==========================")
        for k, v in (self.user_parameters).items():
            logger.log_info(f"{k}={v}")

    def _print_builtin_parameters(self, logger):
        logger.log_info("RGT Test Parameters - Builtin")
        logger.log_info("=============================")
        for k, v in (self.builtin_parameters).items():
            logger.log_info(f"{k}={v}")

    def _set_user_param(self, key, val):
        self.__user_params[key] = val


if __name__ == "__main__":
    print("This is the RgtTest class")
