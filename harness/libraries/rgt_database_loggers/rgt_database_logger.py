#! /usr/bin/env python3

"""
This module implements the database logging capability of the harness.

"""

import os

class RgtDatabaseLogger:

    # This class depends solely on the dictionaries provided to the log_* methods
    # There is no dependence on the subtest or statusfile classes

    # Information required in the log_* methods to be able to send the test information to InfluxDB
    REQUIRED_TEST_INFO = ['test_id', 'app', 'test', 'runtag', 'machine', 'runarchive_dir']

    #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
    #                                                                 @
    # Public methods.                                                 @
    #                                                                 @
    #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

    def __init__(self, logger=None):
        """ 
        Parameters
        ----------
        logger : str
            The rgt_logger of the current scope. Since this class only serves for logging,
            we want it to inherit the logger from the calling class.
        """

        if not logger:
            print("Invalid call to rgt_database_logger constructor: no logger provided")
            return
        self.logger = logger
        self.disabled_backends = self._find_disabled_backends()
        self.enabled_backends = self._add_db_backends()

    def log_event(self, event_dict : dict):
        """
        Logs the provided event to all databases
        """

        if not self._check_test_info_exists(test_info_dict):
            return False

        if self._check_test_disabled_backend(test_info_dict['runarchive_dir']):
            return False

        for backend in self.enabled_backends:
            try:
                backend.send_event(event_dict)
            except Exception as e:
                self.logger.doErrorLogging(f"The following exception occurred while logging an event to {backend.url}: {e.message}.")
                pass

    def log_metrics(self, test_info_dict : dict, metrics_dict : dict):
        """
        Logs the provided event to all databases
        ----
        Parameters:
          test_info_dict : dict
              a dictionary providing test_id, app, test, runtag, machine, and runarchive_dir

          metrics_dict : dict
              a dictionary providing all key-value metrics pairings
        ----
        Returns:
            True if logging is successful for all backends
            False otherwise
        """

        if not self._check_test_info_exists(test_info_dict):
            return False

        if self._check_test_disabled_backend(test_info_dict['runarchive_dir']):
            return False

        for backend in self.enabled_backends:
            try:
                backend.send_metrics(test_info_dict, metrics_dict)
            except Exception as e:
                self.logger.doErrorLogging(f"The following exception occurred while logging metrics to {backend.url}: {e.message}.")
                pass

    def log_node_health(self, test_info_dict : dict, node_health_dict : dict):
        """
        Logs the provided event to all databases
        ----
        Parameters:
          test_info_dict : dict
              a dictionary providing test_id, app, test, runtag, machine, and runarchive_dir

          node_health_dict : dict
              a dictionary providing all node statuses and messages
        ----
        Returns:
            True if logging is successful for all backends
            False otherwise
        """

        if not self._check_test_info_exists(test_info_dict):
            return False

        if self._check_test_disabled_backend(test_info_dict['runarchive_dir']):
            return False

        for backend in self.enabled_backends:
            try:
                backend.send_node_health_results(test_info_dict, node_health_dict)
            except Exception as e:
                self.logger.doErrorLogging(f"The following exception occurred while logging node health results to {backend.url}: {e.message}.")
                pass

    #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
    #                                                                 @
    # End of public methods.                                          @
    #                                                                 @
    #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@


    #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
    #                                                                 @
    # Private methods.                                                @
    #                                                                 @
    #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

    def _check_test_info_exists(self, test_info_dict : dict):
        """
        Checks that all required information exits in the provided test_info_dict
        Parameters
        ----------
            test_info_dict : dict
                A dictionary supplying information about a test needed to log the test
        Returns
        -------
            True if all required information exists
            False otherwise
        """
        provided_keys = list(test_info_dict.keys())
        for key in self.REQUIRED_TEST_INFO:
            if not key in provided_keys:
                self.__logger.doErrorLogging(f'Missing key in provided test info for database logging: {key}')
                return False
        return True

    def _check_test_disabled_backend(self, runarchive_dir : str, db_logger):
        """
        Checks if a specific test has disabled the specified backend
        Checks BOTH environment variables (and creates the dot-files if they don't exist) and the dot-files

        Parameters
        ----------
            runarchive_dir : str
                Path to the Run_Archive directory for the specific test.

            db_logger : instantiation of the base_db class
                Database logger object

        Returns
        -------
            True if test/run has disabled the specific backend
            False otherwise
        """

        # Check if the environment variables to disable the backend are set
        if db_logger.name in self.disabled_backends:
            return True

        # Check if the dot-file exists in Run_Archive/test_id to disable the backend
        # Since the DB backend initialization is NOT done on a per-test basis, it's
        # possible that a test previously had InfluxDB disabled, but was not explicitly
        # disabled in the current environment. We want to enforce the past disabling
        if os.path.exists(os.path.join(runarchive_dir, db_logger.disable_file_name)):
            self.logger.doDebugLogging(f'Found {db_logger.disable_file_name} in {runarchive_dir}. Disabling {db_logger.name}.')
            return True

        return False

    def _find_disabled_backends(self):
        """
        Parses the RGT_DISABLE_* environment variables to add appropriate dot-files to disable database logging

        Returns
        -------
            A list of explicitly-disabled backends
        """
        disabled_backends = []
        if 'RGT_DISABLE_INFLUXDB' in os.environ and str(os.environ['RGT_DISABLE_INFLUXDB']) == '1':
            self.logger.doInfoLogging("InfluxDB logging is explicitly disabled with RGT_DISABLE_INFLUXDB=1")
            disabled_backeds.append('influxdb')
        return disabled_backends

    def _add_db_backends(self):
        """
        Parses the available environment variables to enable specific backends

        Returns
        -------
            A list of enabled backends
        """
        db_backends = []

        # Load InfluxDB now, because we use templated env-vars
        influxdb_loaded = False
        try:
            from db_backends.rgt_influxdb import influxdb_logger
            influxdb_loaded = True
        except ImportError as e:
            self.logger.doErrorLogging(f"The following exception occurred while loading InfluxDB: {e.message}.")
            pass

        if ( influxdb_logger.kw['uri'] in os.environ and influxdb_logger.kw['token'] in os.environ ) \
                and not 'influxdb' in self.disabled_backends \
                and influxdb_loaded:
            # Then we enable InfluxDB
            # Fields for multiple InfluxDB databases can be separated by semicolons
            influxdb_uris = os.environ[influxdb_logger.kw['uri']].split(';')
            influxdb_tokens = os.environ[influxdb_logger.kw['token']].split(';')
            if not len(influxdb_uris) == len(influxdb_tokens):
                self.logger.doErrorLogging("The number of InfluxDB URI's provided does not match the number of InfluxDB tokens. Skpping.")
            else:
                if influxdb_loaded:
                    for i in range(0,len(influxdb_uris)):
                        try:
                            influxdb_backend = influxdb_logger(uri=influxdb_uris[i], token=influxdb_tokens[i], logger=self.logger, subtest=self.subtest)
                            self.enabled_backends.append(influxdb_backend)
                        except DatabaseInitError as e:
                            self.logger.doErrorLogging(e.message)

        return db_backends

    #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
    #                                                                 @
    # End of private methods.                                         @
    #                                                                 @
    #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
