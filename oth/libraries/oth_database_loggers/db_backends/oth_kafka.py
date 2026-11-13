import copy
import glob

# for json.dumps, used to send json object to kafka
import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path

from confluent_kafka import KafkaException, Producer
from confluent_kafka.admin import AdminClient

from .base_db import BaseDBLogger


class KafkaLogger(BaseDBLogger):
    """
    The logging class for Apache Kafka stream processing system
    """

    # Columns to include in events, metrics, and node health records
    KAFKA_COMMON_TEST_FIELDS = [  # noqa: RUF012
        "test_id",
        "app",
        "test",
        "runtag",
        "machine",
        "event_time",
        "job_id",
    ]

    # This list is a subset of what is available, to avoid logging extra columns that don't help
    # For example, since we log runtag, we don't log oth_system_log_tag
    KAFKA_EVENT_FIELDS = KAFKA_COMMON_TEST_FIELDS + [
        "build_directory",
        "event_filename",
        "event_name",
        "event_value",
        "check_alias",
        "hostname",
        "job_account_id",
        "path_to_oth_package",
        "oth_path_to_sspace",
        "run_archive",
        "workdir",
        "user",
        "comment",
        "output_txt",
    ]

    DISABLE_DOTFILE_NAME = ".disable_kafka"
    SUCCESSFUL_DOTFILE_NAME = ".success_kafka"

    # @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
    #                                                                 @
    # Special methods                                                 @
    #                                                                 @
    # @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

    def __init__(
        self,
        uri="",
        username="",
        password="",
        topics=None,
        db_type="",
        db_uri="",
        ssl_ca_loc="",
        ssl_cert_loc="",
        logger=None,
        check_health=True,
    ):

        # Initialize parent so that config vars are accessible
        super().__init__()

        # This function can't be reached except through the parent
        # oth_database_logger, which checks if the logger is not None
        self.__logger = logger
        self.uri = uri
        self.url = uri
        self.username = username
        self.password = password
        # Gets rid of "None" entries, which will be provided by the default constructor
        self.topics = {k: v for k, v in topics.items() if v}
        self.db_type = db_type
        self.db_uri = db_uri
        self.ssl_ca_loc = ssl_ca_loc
        self.ssl_cert_loc = ssl_cert_loc
        self.dryrun = False
        self.check_health = check_health

        self._validate_uri()

        self.conf = {
            "bootstrap.servers": self.uri,
            "security.protocol": "SASL_SSL",
            "sasl.mechanism": "PLAIN",
            "sasl.username": self.username,
            "sasl.password": self.password,
            "ssl.ca.location": self.ssl_ca_loc,
            "ssl.certificate.location": self.ssl_cert_loc,
        }

        if self.check_health:
            alive_msg = self.is_alive()
            if alive_msg:
                message = f"The Kafka server at {self.uri} is not alive or does not have all expected topics: {alive_msg}"
                raise ValueError(message)

        self.producer = Producer(self.conf)

    # @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
    #                                                                 @
    # End of special methods                                          @
    #                                                                 @
    # @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

    # @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
    #                                                                 @
    # Public methods.                                                 @
    #                                                                 @
    # @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

    @property
    def disable_file_name(self):
        return self.DISABLE_DOTFILE_NAME

    @property
    def successful_file_name(self):
        return self.SUCCESSFUL_DOTFILE_NAME

    @property
    def name(self):
        return "kafka"

    def send_event(self, event_dict: dict):
        """
        Posts the event to Kafka.
        """
        if not "events" in self.topics:
            self.__logger.log_warning(
                f"The events topic is not initialized in Kafka logger {self.uri}. Skipping event logging."
            )
            return False

        self.__logger.log_debug(
            f"Posting event {event_dict['event_name']} for test id: {event_dict['test_id']} to Kafka"
        )

        if not "output_txt" in event_dict:
            # Add handling for pasting outputs to influxdb
            if event_dict["event_name"] == "build_end":
                file_name = os.path.join(
                    event_dict["build_directory"], "output_build.txt"
                )
                self.__logger.log_debug(f"Using {file_name} for build output for Kafka")
                if Path(file_name).exists():
                    with open(file_name, "r") as f:
                        output = f.read()
                        # Truncate to 1 KB
                        event_dict["output_txt"] = output[-1024:].replace('"', '\\"')
                else:
                    event_dict["output_txt"] = f"Output file not found in {file_name}"
            elif event_dict["event_name"] == "submit_end":
                file_name = os.path.join(event_dict["run_archive"], "submit.err")
                self.__logger.log_debug(
                    f"Using {file_name} for submit errors for Kafka"
                )
                if Path(file_name).exists():
                    with open(file_name, "r") as f:
                        output = f.read()
                        # Truncate to 1 KB
                        event_dict["output_txt"] = output[-1024:].replace('"', '\\"')
                else:
                    event_dict["output_txt"] = f"Output file not found in {file_name}"
            elif event_dict["event_name"] == "binary_execute_end":
                found_job_file = False
                for file_name in glob.glob(
                    event_dict["run_archive"] + "/*.o" + event_dict["job_id"]
                ):
                    self.__logger.log_debug(
                        f"Using {file_name} for job output for Kafka"
                    )
                    if Path(file_name).exists() and not found_job_file:
                        found_job_file = True
                        with open(file_name, "r") as f:
                            output = f.read()
                            # Truncate to 1 KB
                            event_dict["output_txt"] = output[-1024:].replace(
                                '"', '\\"'
                            )
                if not found_job_file:
                    event_dict["output_txt"] = "No binary execute output files found."
            elif event_dict["event_name"] == "check_end":
                file_name = os.path.join(event_dict["run_archive"], "output_check.txt")
                self.__logger.log_debug(f"Using {file_name} for check output for Kafka")
                if Path(file_name).exists():
                    with open(file_name, "r") as f:
                        output = f.read()
                        # Truncate to 1 KB
                        event_dict["output_txt"] = output[-1024:].replace('"', '\\"')
                else:
                    # if the update_databases wrapper calls this method, then it will provide an output_txt
                    event_dict["output_txt"] = f"Output file not found in {file_name}"
            else:
                # Even if event is not one with an output file, still log the output_txt column
                event_dict["output_txt"] = self.NO_VALUE

        # query_dict is a copy of event_dict, but holding only the information to send
        query_dict = {
            k: event_dict.get(k, self.NO_VALUE) for k in self.KAFKA_EVENT_FIELDS
        }
        query_dict["timestamp"] = self._event_time_to_timestamp(
            query_dict["event_time"]
        )
        # Send message to Kafka & return the result True/False
        return self._send_message(self.topics["events"], query_dict)

    def send_metrics(self, test_info_dict: dict, metrics_dict: dict):
        """
        Posts metrics to Kafka.
        """
        if not "metrics" in self.topics:
            self.__logger.log_warning(
                f"The metrics topic is not initialized in Kafka logger {self.uri}. Skipping metrics logging."
            )
            return False

        self.__logger.log_debug(
            f"Posting metrics from test id: {test_info_dict['test_id']} to Kafka"
        )

        # Put metrics into a fixed-column format, where each metric results in a single message to Kafka
        for metric_name, metric_value in metrics_dict.items():
            # pull info out of test_info_dict that we need & add metrics info
            query_dict = {k: test_info_dict[k] for k in self.KAFKA_COMMON_TEST_FIELDS}
            query_dict["timestamp"] = self._event_time_to_timestamp(
                query_dict["event_time"]
            )
            # For Kafka, we want to un-do the name mangling we do in apptest.py for <app>-<test>-<metric_name>
            query_dict["metric_name"] = metric_name.replace(
                f"{test_info_dict['app']}-{test_info_dict['test']}-", ""
            )
            if self._is_numeric(metric_value):
                query_dict["metric_value"] = float(metric_value)
            else:
                query_dict["metric_value"] = metric_value
            self._send_message(self.topics["metrics"], query_dict, synchronous=False)

        # flush the producer
        nmsgs = self.producer.flush()
        # Send message to Kafka & return the result True/False
        return nmsgs == 0

    def send_node_health_results(self, test_info_dict: dict, node_health_dict: dict):
        """
        Send node health data to Kafka
        """
        if not "node_health" in self.topics:
            self.__logger.log_warning(
                f"The node_health topic is not initialized in Kafka logger {self.uri}. Skipping node_health logging."
            )
            return False

        self.__logger.log_debug(
            f"Posting node health data from test id: {test_info_dict['test_id']} to Kafka"
        )

        # Required environment variable: OTHCTL_NODE_LOCATION_FILE
        if not self.othctl_runtime_config.node_metadata_file:
            raise ValueError(
                "OTHCTL_NODE_LOCATION_FILE required to enable node health logging"
            )

        # on frontier, xname encodes cabinet, chassis, rack, and board information (ie, complete location information)
        required_location_identifiers = ["xname"]

        # find and read node location file -- json file
        use_node_location_file = True

        if self.othctl_runtime_config.node_metadata_file.lower() == "none":
            use_node_location_file = False
        else:
            # else, we assume it is a path and we look for it
            if not Path(self.othctl_runtime_config.node_metadata_file).exists():
                raise ValueError(
                    f"An OTHCTL_NODE_LOCATION_FILE does not exist at {self.othctl_runtime_config.node_metadata_file}"
                )

        node_locations = {}
        # Check if it's a file in valid JSON format -- if it fails, then the oth_db_logger class will catch it
        if use_node_location_file:
            with open(self.othctl_runtime_config.node_metadata_file, "r") as f:
                # if this generates an exception, it will be caught by parent class
                node_locations = json.loads(f.read())

        # for each node found in the nodecheck.txt
        for node_name, node_status in node_health_dict.items():
            # Node health & test info
            # Version 3.9 has the nice and clean pipe operator to merge 2 dictionaries
            if sys.version_info[0] >= 3 and sys.version_info[1] >= 9:  # noqa: YTT203
                query_dict = node_status | {
                    k: test_info_dict[k] for k in self.KAFKA_COMMON_TEST_FIELDS
                }
            else:
                query_dict = copy.deepcopy(node_status)
                for k in self.KAFKA_COMMON_TEST_FIELDS:
                    query_dict[k] = test_info_dict[k]

            query_dict["node"] = node_name
            query_dict["timestamp"] = self._event_time_to_timestamp(
                query_dict["event_time"]
            )
            # Now add location info
            if node_name in node_locations:
                for loc_id in required_location_identifiers:
                    if not loc_id in node_locations[node_name]:
                        self.__logger.log_error(
                            f"Required location identifier {loc_id} not found for node {node_name}. Aborting node health logging."
                        )
                    else:
                        query_dict[loc_id] = node_locations[node_name][loc_id]
            elif use_node_location_file:
                # If we were supposed to use a node location file, but couldn't find info for this node
                self.__logger.log_error(
                    f"Could not find node location information for {node_name}. Aborting node health logging."
                )
                return False
            else:
                # still set these so that all records have consistent schema
                for loc_id in required_location_identifiers:
                    query_dict[loc_id] = self.NO_VALUE

            # Send message to Kafka
            ret = self._send_message(
                self.topics["node_health"], query_dict, synchronous=False
            )
            if not ret:
                # then flush the producer & exit
                self.producer.flush()
                self.__logger.log_error(
                    "Kafka message failed to send. Aborting node health logging."
                )
                return False
        # flush the producer to clear all messages
        nmsgs = self.producer.flush()
        return nmsgs == 0

    def send_external_metrics(
        self, table: str, tags: dict, values: dict, log_time: str
    ):
        """
        Posts external metrics to Kafka.
        """

        self.__logger.log_debug("Posting external metrics to Kafka")

        # Add time to the query dictionary
        query_dict = {**tags, **values}
        query_dict["time"] = log_time
        # Kafka also wants a timestamp:
        query_dict["timestamp"] = self._event_time_to_timestamp(log_time)

        # Send message to Kafka & return the result True/False
        return self._send_message(table, query_dict)

    def is_alive(self):
        """
        Check if each of the provided topics exists in the Kafka instance
        """
        self.__logger.log_debug(
            f"Checking for the following topics for Kafka health check and topic verification: {','.join(self.topics.values())} at {self.uri}"
        )

        err_msg = None
        # requires broker v0.11 or later
        try:
            test_client = AdminClient(self.conf)
            for t in self.topics:
                response = test_client.list_topics(topic=self.topics[t], timeout=10)
                if response.topics[self.topics[t]].error:
                    return f"Couldn't find topic {self.topics[t]} in Kafka instance. Error: {response.topics[self.topics[t]].error}"
        except KafkaException as e:
            err_msg = f"A Kafka Exception occured while checking if the server is alive: {e!s}"
        except Exception as e:  # noqa: BLE001
            err_msg = (
                f"An Exception occured while checking if the server is alive: {e!s}"
            )

        return err_msg

    def query(self, query):
        """
        Parameters:
            query: a query string

        Returns:
            a list of dictionary objects
        """
        if self.db_type.upper() == "DRUID":
            return self._query_druid(query)
        else:
            self.__logger.log_critical(
                "The Kafka db_logger backend does not support the query() method for any database backend except Druid yet. Support is enabled for Druid via the OTHCTL_KAFKA_DB_TYPE=Druid and OTHCTL_KAFKA_DB_URI fields."
            )
            return []

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

    def _validate_uri(self):
        """
        Parses environment variables set for OTHCTL_KAFKA_* and tests the connection
        """

        # The only Kafka variable that isn't parsed by the parent database handler is dryrun
        # All other fields are allowed to be semicolon-separated (for multiple instances),
        # so they must be parsed outside of here
        if self.othctl_runtime_config.kafka_disable == "1":
            self.dryrun = True

        # Even though we don't set self.topics here, we can still check that it's non-empty
        # NOTE -- topics is not required to be length-3. If the metrics topic is not defined,
        # then it is disabled, and a warning will be printed
        if len(self.topics) == 0:
            message = (
                "No Kafka topics could be found in the harness Kafka configurations."
            )
            raise ValueError(message)

    def _send_message(self, topic: str, payload: dict, synchronous: bool = True):
        """
        Sends the message to InfluxDB with the associated headers
        """

        if self.dryrun:
            self.__logger.log_info(f"Kafka dry-run is set. Message: {payload}")
            return True

        # validate the payload dict to make sure certain fields exist:
        if not "timestamp" in payload:
            raise ValueError(
                f"Payload dictionary does not contain a 'timestamp' field when sending to Kafka topic {topic}: {payload}"
            )

        self.__logger.log_debug(f"Sending message to Kafka topic {topic}: {payload}")

        self.producer.produce(topic, value=json.dumps(payload))

        if synchronous:
            nmsgs = self.producer.flush()
            if nmsgs == 0:
                return True

        # if synchronous = False is specified, it's the user's job to flush the producer
        return True

    def _query_druid(self, query):
        """
        Parameters:
            query: a SQL query string

        Returns:
            a list of dictionary objects
        """
        # this is a helper method that queries Druid and returns the result
        # Druid querying needs the `requests` module, as opposed to Kafka, which does not
        # so we separate the import into this method
        import requests

        query_data = {"query": query}

        self.__logger.log_info(f"Querying Druid database with query: {query}.")

        response = requests.post(
            f"{self.db_uri}/druid/v2/sql",
            json=query_data,
            auth=(self.username, self.password),
            headers={"Content-Type": "application/json"},
        )

        try:
            response.raise_for_status()
            self.__logger.log_debug(f"Query completed successfully: {query}")
            self.__logger.log_debug(f"Query response: {response.json()}")
            return response.json()
        except requests.exceptions.RequestException as e:
            self.__logger.log_error(f"Druid Query failed: {e!s}.")
            # continue raising this error to propagate the failure
            raise

    def _event_time_to_timestamp(self, event_time: str):
        """Converts a time string to Unix timestamp in EST"""

        # Check for different time formats
        if re.search(
            r"^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}\.[0-9]{6}$",
            event_time,
        ):
            # YYYY-MM-DDTHH:MM:SS.UUUUUU -- this is the default harness output
            log_time = datetime.strptime(event_time, "%Y-%m-%dT%H:%M:%S.%f")  # noqa: DTZ007
        elif re.search(
            r"^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}\.[0-9]{3}Z$",
            event_time,
        ):
            # YYYY-MM-DDTHH:MM:SS.mmmZ
            log_time = datetime.strptime(event_time, "%Y-%m-%dT%H:%M:%S.%fZ")  # noqa: DTZ007
        elif re.search(
            r"^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}\.[0-9]{6}Z$",
            event_time,
        ):
            # YYYY-MM-DDTHH:MM:SS.UUUUUUZ
            log_time = datetime.strptime(event_time, "%Y-%m-%dT%H:%M:%S.%fZ")  # noqa: DTZ007
        elif re.search(
            r"^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}$",
            event_time,
        ):
            # YYYY-MM-DDTHH:MM:SS
            log_time = datetime.strptime(event_time, "%Y-%m-%dT%H:%M:%S")  # noqa: DTZ007
        elif re.search(
            r"^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z$",
            event_time,
        ):
            # YYYY-MM-DDTHH:MM:SSZ
            log_time = datetime.strptime(event_time, "%Y-%m-%dT%H:%M:%S")  # noqa: DTZ007
        else:
            raise ValueError(f"Unrecognized time format in string {event_time}.")

        # Kafka wants timestamps in seconds, for indexing only (not unique identifiers)
        return int(datetime.timestamp(log_time))
