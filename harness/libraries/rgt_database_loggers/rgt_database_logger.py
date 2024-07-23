#! /usr/bin/env python3

"""
This module implements the database logging capability of the harness.

"""

import os

class rgt_database_logger:

    # This class is entirely parameterized by environment variables and dot-files in a test's Run_Archive directory,
    # which enable/disable various database backends
    # ie, RGT_INFLUX_URI

    def __init__(self, logger=None, subtest=None):
        """ 
        Parameters
        ----------
        logger : str
            The rgt_logger of the current scope. Since this class only serves for logging,
            we want it to inherit the logger from the calling class.

        subtest : subtest
            The subtest associated with this database logger
        """

        if not logger:
            print("Invalid call to rgt_database_logger constructor: no logger provided")
            return
        self.logger = logger
        if not subtest:
            self.logger.doErrorLogging("Invalid call to rgt_database_logger constructor: no apptest provided")
        self.subtest = subtest
        self.disabled_backends = self._find_disabled_backends()
        self.enabled_backends = self._add_db_backends()

    # Private methods
    def _find_disabled_backends(self):
        """
        Parses the RGT_DISABLE_* environment variables to add appropriate dot-files to disable database logging
        """
        disabled_backends = []
        if 'RGT_DISABLE_INFLUXDB' in os.environ and str(os.environ['RGT_DISABLE_INFLUXDB']) == '1':
            self.logger.doWarningLogging("InfluxDB logging is explicitly disabled with RGT_DISABLE_INFLUXDB=1")
            self.logger.doInfoLogging(f"Creating .disable_influxdb file in {os.path.join(self.subtest.get_path_to_runarchive(), '.disable_influxdb')}")
            self.logger.doInfoLogging("If this was not intended, remove the .disable_influxdb file and run the harness under mode 'influx_log'")
            os.mknod(os.path.join(self.subtest.get_path_to_runarchive(), '.disable_influxdb'))
        # Check in a separate if, since the file could already exist without environment variables being set
        if os.path.exists(os.path.join(self.subtest.get_path_to_runarchive(), '.disable_influxdb')):
            self.logger.doInfoLogging("Found a .disable_influxdb dot-file, disabling all InfluxDB logging")
            disabled_backeds.append('influxdb')
        return disabled_backends

    def _add_db_backends(self):
        """
        Parses the available environment variables to enable specific backends
        """
        db_backends = []

        # Load InfluxDB now, because we use templated env-vars
        influxdb_loaded = False
        try:
            from db_backends.influxdb import influxdb_logger
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
