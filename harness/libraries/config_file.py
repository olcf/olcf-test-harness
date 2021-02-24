import string
import os
import configparser

from rgt_utilities import set_harness_environment

class rgt_config_file:

    # These are the named sections in the config file.
    machine_section    = 'MachineDetails'
    repository_section = 'RepoDetails'
    testshot_section   = 'TestshotDefaults'

    def __init__(self,
                 configfilename=None,
                 machinename=None):

        self.__machine_vars = {}
        self.__repo_vars = {}
        self.__testshot_vars = {}

        if machinename != None:
            self.__configFileName = machinename + ".ini"
        else:
            if configfilename == None:
                configfilename = self.getDefaultConfigFile()
            self.__configFileName = configfilename

        base_filename = os.path.basename(self.__configFileName)
        if base_filename == self.__configFileName:
            # Only base file given, resolve full path by searching CWD, then OLCF_HARNESS_DIR/configs
            working_dir_config = os.path.join(os.getcwd(), self.__configFileName)
            if os.path.isfile(working_dir_config):
                self.__configFileName = os.path.abspath(working_dir_config)
            elif 'OLCF_HARNESS_DIR' in os.environ:
                harness_dir = os.environ['OLCF_HARNESS_DIR']
                harness_dir_config = os.path.join(harness_dir, "configs", self.__configFileName)
                if os.path.isfile(harness_dir_config):
                    self.__configFileName = harness_dir_config

        # Read the master config file
        self.__read_config_file()

    def __read_config_file(self):
        if os.path.isfile(self.__configFileName):
            print(f'reading harness config {self.__configFileName}')
            master_cfg = configparser.ConfigParser()
            master_cfg.read(self.__configFileName)

            self.__machine_vars = master_cfg[rgt_config_file.machine_section]
            set_harness_environment(self.__machine_vars)

            self.__repo_vars = master_cfg[rgt_config_file.repository_section]
            set_harness_environment(self.__repo_vars)

            self.__testshot_vars = master_cfg[rgt_config_file.testshot_section]
            set_harness_environment(self.__testshot_vars)
        else:
            raise NameError("Harness config file not found: %s" % self.__configFileName)

    def get_config_file(self):
        return self.__configFileName

    def get_machine_config(self):
        return self.__machine_vars

    def get_repository_config(self):
        return self.__repo_vars

    def get_testshot_config(self):
        return self.__testshot_vars

    @staticmethod
    def getDefaultConfigFile():
        """Returns the default config file name."""
        machinename = 'master'
        if 'OLCF_HARNESS_MACHINE' in os.environ:
            machinename = os.environ['OLCF_HARNESS_MACHINE']
        configfile = machinename + '.ini'
        print('Using machine config:', configfile)
        return configfile

