"""
This module implements the database logging capability of the harness.

"""

import os
from pathlib import Path


class OthDatabaseLogger:
    # This class depends solely on the dictionaries provided to the log_* methods
    # There is no dependence on the subtest or statusfile classes

    # Information required in the log_* methods to be able to send the test information to any database
    REQUIRED_TEST_INFO = ["test_id", "app", "test", "runtag", "machine"]  # noqa: RUF012

    # @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
    #                                                                 @
    # Public methods.                                                 @
    #                                                                 @
    # @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

    def __init__(self, logger=None, only=None):
        """
        Parameters
        ----------
        logger : oth_logger
            The oth_logger of the current scope. Since this class only serves for logging,
            we want it to inherit the logger from the calling class.
        only : str
            (Optional) a string URL for a specific database backend to initialize
        """

        from oth.config import othctl_runtime_config

        self.othctl_runtime_config = othctl_runtime_config

        if not logger:
            print("Invalid call to oth_database_logger constructor: no logger provided")
            return
        self.logger = logger
        self.disabled_backends = []  # strings -- "influxdb", "kafka", etc
        self.disabled_backends_filenames = []  # strings -- ".disable_influxdb", etc
        self._find_disabled_backends()
        self.enabled_backends = []  # database logger objects
        self._add_db_backends(only=only)

    def log_event(self, event_dict: dict, only=None):
        """
        Logs the provided event to all databases
        ----
        Parameters:
          event_dict : dict
              a dictionary providing all event information to log
          only : str
              a string URL specifying which database backend to log to (defaults to logging to all)
        """

        if not self._check_test_info_exists(event_dict):
            return False

        # Go to the Run_Archive directory to be consistent with metrics & node health logging
        currentdir = os.getcwd()
        runarchive_dir = event_dict["run_archive"]
        os.chdir(runarchive_dir)

        # Use event file name to match the logging_start event
        if event_dict["event_name"] == "logging_start":
            # Make sure that any explicitly-disabled backends create the dot-file
            for dotfile in self.disabled_backends_filenames:
                if not Path(dotfile).exists():
                    os.mknod(dotfile)

        num_failed = 0

        for backend in self._make_db_target_list(only):
            try:
                if not self._check_test_disabled_backend(backend):
                    if not backend.send_event(event_dict):
                        self.logger.log_error(
                            f"An error occurred while logging an event to {backend.url}. Please see log files for more details."
                        )
                        num_failed += 1
                    elif (
                        event_dict["event_name"] == "check_end"
                        and not Path(backend.successful_file_name).exists()
                    ):
                        # If we just successfully logged check_end, then we add a dot-file to indicate logging completed
                        os.mknod(backend.successful_file_name)
            except Exception as e:  # noqa: BLE001
                self.logger.log_error(
                    f"The following exception occurred while logging an event to {backend.url}: {e}."
                )
                num_failed += 1

        os.chdir(currentdir)
        return num_failed == 0

    def log_metrics(self, test_info_dict: dict, metrics_dict: dict, only=None):
        """
        Logs the provided metrics data to all databases
        ----
        Parameters:
          test_info_dict : dict
              a dictionary providing test_id, app, test, runtag, machine

          metrics_dict : dict
              a dictionary providing all key-value metrics pairings

          only : str
              a string URL specifying which database backend to log to (defaults to logging to all)
        ----
        Returns:
            True if logging is successful for all backends
            False otherwise
        """

        if not self._check_test_info_exists(test_info_dict):
            return False

        num_failed = 0

        for backend in self._make_db_target_list(only):
            try:
                if not (
                    self._check_test_disabled_backend(backend)
                    or backend.send_metrics(test_info_dict, metrics_dict)
                ):
                    self.logger.log_error(
                        f"An error occurred while logging an metrics to {backend.url}. Please see log files for more details."
                    )
                    num_failed += 1
            except Exception as e:  # noqa: BLE001
                self.logger.log_error(
                    f"The following exception occurred while logging metrics to {backend.url}: {e}."
                )
                num_failed += 1
        return num_failed == 0

    def log_node_health(self, test_info_dict: dict, node_health_dict: dict, only=None):
        """
        Logs the provided event to all databases
        ----
        Parameters:
          test_info_dict : dict
              a dictionary providing test_id, app, test, runtag, machine

          node_health_dict : dict
              a dictionary providing all node statuses and messages

          only : str
              a string URL specifying which database backend to log to (defaults to logging to all)
        ----
        Returns:
            True if logging is successful for all backends
            False otherwise
        """

        if not self._check_test_info_exists(test_info_dict):
            return False

        num_failed = 0
        for backend in self._make_db_target_list(only):
            try:
                if not (
                    self._check_test_disabled_backend(backend)
                    or backend.send_node_health_results(
                        test_info_dict, node_health_dict
                    )
                ):
                    self.logger.log_error(
                        f"An error occurred while logging node health data to {backend.url}. Please see log files for more details."
                    )
                    num_failed += 1
            except Exception as e:  # noqa: BLE001
                self.logger.log_error(
                    f"The following exception occurred while logging node health results to {backend.url}: {e}."
                )
                num_failed += 1
        return num_failed == 0

    def log_external_metrics(
        self, table: str, tags: dict, values: dict, log_time: str, only=None
    ):
        """
        Logs the provided external metrics to the databases
        ----
        Parameters:
          table : str
              The table/measurement to log this data to

          tags : dict
              A dictionary providing all tags to log the data under

          values : dict
              A dictionary providing all data to log

          log_time : str
              The timestamp (isoformat) to associate with this metric
        ----
        Returns:
            True if logging is successful for all backends
            False otherwise
        """

        # Logging external metrics is very simple -- just do it. No dot-files, just environment variables
        num_failed = 0
        for backend in self._make_db_target_list(only):
            try:
                if not backend.send_external_metrics(table, tags, values, log_time):
                    self.logger.log_error(
                        f"An error occurred while logging external metrics to {backend.url}. Please see log files for more details."
                    )
                    num_failed += 1
            except Exception as e:  # noqa: BLE001
                self.logger.log_error(
                    f"The following exception occurred while logging external metrics to {backend.url}: {e}."
                )
                num_failed += 1
        return num_failed == 0

    # @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
    #                                                                 @
    # End of public methods.                                          @
    #                                                                 @
    # @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

    # @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
    #                                                                 @
    # Private methods.                                                @
    #                                                                 @
    # @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

    def _check_test_info_exists(self, test_info_dict: dict):
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
                self.logger.log_error(
                    f"Missing key in provided test info for database logging: {key}"
                )
                return False
        return True

    def _check_test_disabled_backend(self, db_logger):
        """
        Checks if a specific test has disabled the specified backend
        Checks BOTH environment variables (and creates the dot-files if they don't exist) and the dot-files
        This function should be called from the Run_Archive directory

        Parameters
        ----------
            db_logger : instantiation of the base_db class
                Database logger object

        Returns
        -------
            True if test/run has disabled the specific backend
            False otherwise
        """

        # Check if the environment variables to disable the backend are set
        if db_logger.name in self.disabled_backends:
            # Create dot-file if it doesn't already exist
            if not Path(db_logger.disable_file_name).exists():
                os.mknod(db_logger.disable_file_name)
            return True

        # Check if the dot-file exists in Run_Archive/test_id to disable the backend
        # Since the DB backend initialization is NOT done on a per-test basis, it's
        # possible that a test previously had InfluxDB disabled, but was not explicitly
        # disabled in the current environment. We want to enforce the past disabling
        if Path(db_logger.disable_file_name).exists():
            self.logger.log_debug(
                f"Found {db_logger.disable_file_name} in {os.getcwd()}. Disabling {db_logger.name}."
            )
            return True

        return False

    def _make_db_target_list(self, only=None):
        """
        Creates the list of databases to send messages to
        Optionally with a string URL specifier (only)

        Parameters
        ----------
            only : string
                (Optional) string specifying the URL of the database to select

        Returns
        -------
            A list of databases matching the criteria to iterate over
        """
        if not only:
            return self.enabled_backends
        db_list = []
        for db in self.enabled_backends:
            if db.url == only:
                db_list.append(db)
        if len(db_list) == 0:
            self.logger.log_warning(
                f"Found no database backends matching the URL {only}"
            )
        return db_list

    def _find_disabled_backends(self):
        """
        Parses the OTHCTL_* environment variables to add appropriate dot-files to disable database logging

        Returns
        -------
            A list of explicitly-disabled backends
        """
        # Load InfluxDB now, because we use templated env-vars
        influxdb_loaded = False
        try:
            from oth.libraries.oth_database_loggers.db_backends.oth_influxdb import (
                InfluxDBLogger,
            )

            influxdb_loaded = True
        except ImportError as e:
            self.logger.log_error(f"Failed to import InfluxDB backend: {e}.")

        if influxdb_loaded and self.othctl_runtime_config.influxdb_disable == "1":
            self.logger.log_info("InfluxDB logging is explicitly disabled.")
            self.disabled_backends.append("influxdb")
            self.disabled_backends_filenames.append(InfluxDBLogger.DISABLE_DOTFILE_NAME)

    def _add_db_backends(self, only=None):
        """
        Parses the available environment variables to enable specific backends

        Parameters
        ----------
            only : string
                (Optional) string specifying the URL of the database to select

        Returns
        -------
            None
        """
        # Load InfluxDB now, because we use templated env-vars
        influxdb_loaded = False
        kafka_loaded = False

        if any(k.startswith("OTHCTL_INFLUX") for k in os.environ):
            try:
                # Can fail for a number of reasons. Mostly if `requests` module is not installed
                from oth.libraries.oth_database_loggers.db_backends.oth_influxdb import (
                    InfluxDBLogger,
                )

                influxdb_loaded = True
            except ImportError as e:
                self.logger.log_error(f"Failed to import InfluxDB backend: {e}")

        if any(k.startswith("OTHCTL_KAFKA") for k in os.environ):
            try:
                # Can fail for a number of reasons. Mostly if `requests` module is not installed
                from oth.libraries.oth_database_loggers.db_backends.oth_kafka import (
                    KafkaLogger,
                )

                kafka_loaded = True
            except ImportError as e:
                self.logger.log_error(f"Failed to import Kafka backend: {e}")

        if (
            influxdb_loaded
            and not "influxdb" in self.disabled_backends
            and (
                self.othctl_runtime_config.influxdb_uri
                and self.othctl_runtime_config.influxdb_token
            )
        ):
            # Then we enable InfluxDB
            # Fields for multiple InfluxDB databases can be separated by semicolons
            influxdb_uris = self.othctl_runtime_config.influxdb_uri.split(";")
            influxdb_tokens = self.othctl_runtime_config.influxdb_token.split(";")
            if len(influxdb_uris) != len(influxdb_tokens):
                self.logger.log_error(
                    "The number of InfluxDB URI's provided does not match the number of InfluxDB tokens. Skpping."
                )
            elif influxdb_loaded:
                for i in range(len(influxdb_uris)):
                    try:
                        # If you use multiple InfluxDB instances, you must not use the OTHCTL_INFLUXDB_BUCKET or OTHCTL_INFLUXDB_ORG variables
                        # unless the same bucket and org name apply to all InfluxDB instances
                        # Otherwise, you should let the InfluxDB logger backend parse the bucket & org from the URL
                        influxdb_backend = InfluxDBLogger(
                            uri=influxdb_uris[i],
                            token=influxdb_tokens[i],
                            logger=self.logger,
                        )
                        if not only or influxdb_backend.url == only:
                            self.logger.log_debug(
                                f"Enabling the {influxdb_backend.name} database logger from URL {influxdb_uris[i]}."
                            )
                            self.enabled_backends.append(influxdb_backend)
                    except Exception as e:  # noqa: BLE001
                        self.logger.log_error(
                            f"Failed to enable the database logger from URL {influxdb_uris[i]}: {e}"
                        )
        if (
            kafka_loaded
            and (not "kafka" in self.disabled_backends)
            and (
                self.othctl_runtime_config.kafka_uri
                and self.othctl_runtime_config.kafka_username
                and self.othctl_runtime_config.kafka_password
                and self.othctl_runtime_config.kafka_events_topic
            )
        ):
            # Then we enable Kafka
            # Fields for multiple Kafka databases can be separated by semicolons
            # the length of kafka_uris is the authoritative source of how many sources are expected

            # required fields:
            kafka_uris = self.othctl_runtime_config.kafka_uri.split(";")
            kafka_usernames = self.othctl_runtime_config.kafka_username.split(";")
            kafka_passwords = self.othctl_runtime_config.kafka_password.split(";")
            kafka_topic_events = self.othctl_runtime_config.kafka_events_topic.split(
                ";"
            )
            # metrics & node health topics are optional
            kafka_topic_metrics = None
            kafka_topic_node_healths = None
            if self.othctl_runtime_config.kafka_metrics_topic:
                kafka_topic_metrics = (
                    self.othctl_runtime_config.kafka_metrics_topic.split(";")
                )
            if self.othctl_runtime_config.kafka_node_health_topic:
                kafka_topic_node_healths = (
                    self.othctl_runtime_config.kafka_node_health_topic.split(";")
                )
            kafka_db_type = self.othctl_runtime_config.kafka_db_type.split(";")
            kafka_db_uri = self.othctl_runtime_config.kafka_db_uri.split(";")
            kafka_ssl_ca_loc = self.othctl_runtime_config.kafka_ssl_ca_location.split(
                ";"
            )
            kafka_ssl_cert_locs = (
                self.othctl_runtime_config.kafka_ssl_certificate_location.split(";")
            )

            for i in range(len(kafka_uris)):
                try:
                    # Kafka requires way more parameterization than InfluxDB...
                    kafka_backend = KafkaLogger(
                        uri=kafka_uris[i],
                        username=kafka_usernames[i],
                        password=kafka_passwords[i],
                        topics={
                            "events": kafka_topic_events[i],
                            "metrics": kafka_topic_metrics[i],
                            "node_health": kafka_topic_node_healths[i],
                        },
                        db_type=kafka_db_type[i],
                        db_uri=kafka_db_uri[i],
                        ssl_ca_loc=kafka_ssl_ca_loc[i],
                        ssl_cert_loc=kafka_ssl_cert_locs[i],
                        logger=self.logger,
                    )
                    if not only or kafka_backend.url == only:
                        self.logger.log_debug(
                            f"Enabling the {kafka_backend.name} database logger from URL {kafka_uris[i]}."
                        )
                        self.enabled_backends.append(kafka_backend)
                except Exception as e:  # noqa: BLE001
                    self.logger.log_error(
                        f"Failed to enable the database logger from URL {kafka_uris[i]}: {e}"
                    )

    # @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
    #                                                                 @
    # End of private methods.                                         @
    #                                                                 @
    # @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
