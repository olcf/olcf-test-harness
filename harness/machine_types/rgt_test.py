"""
.. module:: rgt_test
    :platform: Linux
    :synopsis: Abstracts the regression test input file.

"""
#
# Author: Veronica G. Vergara L.
#

import configparser
import os

class RgtTest():
    """ This class is the abstraction of regression test input file.

    """

    def __init__(self, filename):
        self.__inputfile = filename
        self.__builtin_params = {}
        self.__user_params = {}
        self.__environ = {}
        # dict of builtin keys - value indicates whether it is required
        self.__builtin_keys = {
            "batch_filename" : True,
            "batch_queue" : True,
            "build_cmd" : True,
            "check_cmd": True,
            "executable_path" : False,
            "job_name" : True,
            "nodes" : True,
            "processes_per_node" : False,
            "project_id" : True,
            "report_cmd" : True,
            "resubmit" : False,
            "total_processes" : False,
            "walltime" : True
        }

    def get_test_input_file(self):
        return self.__inputfile

    #
    # Methods to manage builtin parameters
    #

    def is_builtin_param(self, key):
        return key in self.__builtin_keys

    def add_builtin_param(self, key, required, warn=True):
        if key not in self.__builtin_keys:
            self.__builtin_keys[key] = required
            return True
        else:
            if warn:
                print("WARNING: provided key {} is already built-in")
            return False

    def set_builtin_param(self, key, val, warn=True):
        if self.is_builtin_param(key):
            self.__builtin_params[key] = val
            return True
        else:
            if warn:
                print("WARNING: Ignoring invalid built-in parameter key {}".format(key))
            return False

    def get_builtin_param(self, key):
        if key in self.__builtin_params:
            return self.__builtin_params[key]
        else:
            return None

    def set_builtin_parameters(self, params_view):
        for (k,v) in params_view:
            self.set_builtin_param(k, v)

    def print_builtin_parameters(self):
        print("RGT Test Parameters - Builtin")
        print("=============================")
        for (k,v) in self.__builtin_params.items():
            print(k,"=",v)

    def check_required_parameters(self):
        missing = 0
        for (k,required) in self.__builtin_keys.items():
            if required and k not in self.__builtin_params:
                missing = 1
                print("ERROR: required test input parameter {} is not set!".format(k))
        if missing:
            exit(1)

    #
    # Methods to manage user parameters and environment
    #

    def set_user_param(self, key, val):
        self.__user_params[key] = val

    def get_user_param(self, key):
        if key in self.__user_params:
            return self.__user_params[key]
        else:
            return None

    def set_user_parameters(self, params_view):
        # NOTE: usign dict.update() to support append
        self.__user_params.update(params_view)

    def print_user_parameters(self):
        print("RGT Test Parameters - User")
        print("==========================")
        for (k,v) in self.__user_params.items():
            print(k,"=",v)

    #
    # Methods to retrieve full test dictionaries
    #

    def get_test_environment(self):
        return self.__environ

    def set_test_environment(self, envvars_view):
        # NOTE: usign dict.update() to support append
        self.__environ.update(envvars_view)

    def get_test_parameters(self):
        parameters = self.__builtin_params
        parameters.update(self.__user_params)
        return parameters

    def set_test_parameters(self, params_view):
        for (k,v) in params_view:
            if self.is_builtin_param(k):
                self.set_builtin_param(k, v)
            else:
                self.set_user_param(k, v)

    def get_test_replacements(self):
        replacements = {}
        for (k,v) in self.__builtin_params.items():
            replace_key = '__' + k + '__'
            replacements[replace_key] = v
        for (k,v) in self.__user_params.items():
            replace_key = '__' + k + '__'
            replacements[replace_key] = v
        return replacements

    def print_test_parameters(self):
        self.print_builtin_parameters()
        self.print_user_parameters()

    #
    # Convenience methods for retrieving specific parameters
    #

    def get_batch_file(self):
        return self.get_builtin_param("batch_filename")

    def get_batch_queue(self):
        return self.get_builtin_param("batch_queue")

    def get_build_command(self):
        return self.get_builtin_param("build_cmd")

    def get_check_command(self):
        return self.get_builtin_param("check_cmd")

    def get_report_command(self):
        return self.get_builtin_param("report_cmd")

    def get_executable(self):
        return self.get_builtin_param("executable_path")

    def get_jobname(self):
        return self.get_builtin_param("job_name")

    def get_nodes(self):
        return self.get_builtin_param("nodes")

    def get_project(self):
        return self.get_builtin_param("project_id")

    def get_walltime(self):
        return self.get_builtin_param("walltime")

    def get_total_processes(self):
        val = self.get_builtin_param("total_processes")
        if val is None:
            return str(0)
        else:
            return val

    def get_processes_per_node(self):
        val = self.get_builtin_param("processes_per_node")
        if val is None:
            return str(0)
        else:
            return val

    #
    # Input file readers
    #

    def read_input_file(self):
        if os.path.isfile(self.__inputfile):
            basename = os.path.basename(self.__inputfile)
            if basename == "rgt_test_input.txt":
                self.read_rgt_input_txt()
            elif basename == "rgt_test_input.ini":
                self.read_rgt_input_ini()
            else:
                print("ERROR: unsupported test input file name {}".format(basename))
                exit(1)
            self.print_test_parameters()
            self.check_required_parameters()
        else:
            print("ERROR: test input file {} not found".format(self.__inputfile))
            exit(1)

    def read_rgt_input_txt(self):
        params_dict = {}
        delimiter = '='
        fileobj = open(self.__inputfile)
        filelines = fileobj.readlines()
        fileobj.close()
        for line in filelines:
            stripline = line.strip()
            if not stripline or stripline[0] == '#':
                continue
            (k,v) = stripline.split(delimiter)
            params_dict[k.strip().lower()] = v.strip()
        self.set_test_parameters(params_dict.items())

    def read_rgt_input_ini(self):
        rgt_test_config = configparser.ConfigParser()
        rgt_test_config.read(self.__inputfile)

        if not 'Replacements' in rgt_test_config:
            print("ERROR: missing [Replacements] section in test input")
            replace = dict()
        else:
            replace = rgt_test_config['Replacements']
        self.set_test_parameters(replace.items())

        if 'EnvVars' in rgt_test_config:
            env_vars = rgt_test_config['EnvVars']
            self.set_test_environment(env_vars)

if __name__ == "__main__":
    print('This is the RgtTest class')
