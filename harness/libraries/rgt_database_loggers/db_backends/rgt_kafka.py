#! /usr/bin/env python3

import csv
from datetime import datetime
import glob
# for json.dumps, used to send json object to kafka
import json
import os
import re
from confluent_kafka import Producer, KafkaException
from confluent_kafka.admin import AdminClient

from libraries.rgt_database_loggers.db_backends.base_db import *

class KafkaLogger(BaseDBLogger):

    """
    The logging class for Apache Kafka stream processing system
    """

    kw = {
        'uri': 'RGT_KAFKA_URI',
        'username': 'RGT_KAFKA_USERNAME',
        'password': 'RGT_KAFKA_PASSWORD',
        'topic_events': 'RGT_KAFKA_EVENTS_TOPIC',
        'topic_metrics': 'RGT_KAFKA_METRICS_TOPIC',
        'topic_node_health': 'RGT_KAFKA_NODE_HEALTH_TOPIC',
        'db_type': 'RGT_KAFKA_DB_TYPE',
        'db_uri': 'RGT_KAFKA_DB_URI',
        'ssl_ca_loc': 'RGT_KAFKA_SSL_CA_LOCATION',
        'ssl_cert_loc': 'RGT_KAFKA_SSL_CERTIFICATE_LOCATION',
        'dryrun': 'RGT_KAFKA_DRY_RUN',
        'disable': 'RGT_KAFKA_DISABLE'
    }

    # Re-defines the StatusFile.NOVALUE
    NO_VALUE = '[NO_VALUE]'

    # Columns to include in events, metrics, and node health records
    KAFKA_COMMON_TEST_FIELDS = [
                'test_id',
                'app',
                'test',
                'runtag',
                'machine',
                'job_id',
                'event_time'
    ]

    # This list is a subset of what is available, to avoid logging extra columns that don't help
    # For example, since we log runtag, we don't log rgt_system_log_tag
    KAFKA_EVENT_FIELDS = KAFKA_COMMON_TEST_FIELDS + [
                'build_directory',
                'event_filename',
                'event_name',
                'event_value',
                'check_alias',
                'hostname',
                'job_account_id',
                'path_to_rgt_package',
                'rgt_path_to_sspace',
                'run_archive',
                'workdir',
                'user',
                'comment',
                'output_txt'
    ]


    DISABLE_DOTFILE_NAME = '.disable_kafka'
    SUCCESSFUL_DOTFILE_NAME = '.success_kafka'

    #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
    #                                                                 @
    # Special methods                                                 @
    #                                                                 @
    #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

    def __init__(self,
                 uri='',
                 username='',
                 password='',
                 topics={},
                 db_type='',
                 db_uri='',
                 ssl_ca_loc='',
                 ssl_cert_loc='',
                 logger=None):

        # This function can't be reached except through the parent
        # rgt_database_logger, which checks if the logger is not None
        self.__logger = logger
        self.uri = uri
        self.url = uri
        self.username = username
        self.password = password
        # Gets rid of "None" entries, which will be provided by the default constructor
        self.topics = {k: v for k,v in topics.items() if v}
        self.db_type = db_type
        self.db_uri = db_uri
        self.ssl_ca_loc = ssl_ca_loc
        self.ssl_cert_loc = ssl_cert_loc
        self.dryrun = False

        self._validate_uri()

        self.conf = {
            'bootstrap.servers': self.uri,
            'security.protocol': 'SASL_SSL',
            'sasl.mechanism': 'PLAIN',
            'sasl.username': self.username,
            'sasl.password': self.password,
            'ssl.ca.location': self.ssl_ca_loc,
            'ssl.certificate.location': self.ssl_cert_loc
        }

        alive_msg = self.is_alive()
        if alive_msg:
            message = f'The Kafka server at {self.uri} is not alive or does not have all expected topics: {alive_msg}'
            raise DatabaseInitError(message)

        self.producer = Producer(self.conf)

    #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
    #                                                                 @
    # End of special methods                                          @
    #                                                                 @
    #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@


    #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
    #                                                                 @
    # Public methods.                                                 @
    #                                                                 @
    #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

    @property
    def disable_file_name(self):
        return self.DISABLE_DOTFILE_NAME

    @property
    def disable_envvar_name(self):
        return self.kw['dryrun']

    @property
    def successful_file_name(self):
        return self.SUCCESSFUL_DOTFILE_NAME

    @property
    def name(self):
        return 'kafka'

    def send_event(self, event_dict : dict):
        """
            Posts the event to Kafka.
        """
        if not 'events' in self.topics:
            self.__logger.doWarningLogging(f"The events topic is not initialized in Kafka logger {self.uri}. Skipping event logging.")
            return False

        self.__logger.doDebugLogging(f"Posting event {event_dict['event_name']} for test id: {event_dict['test_id']} to Kafka")

        if not 'output_txt' in event_dict.keys():
            # Add handling for pasting outputs to influxdb
            if event_dict['event_name'] == "build_end":
                file_name = os.path.join(event_dict['build_directory'], "output_build.txt")
                self.__logger.doDebugLogging(f"Using {file_name} for build output for Kafka")
                if os.path.exists(file_name):
                    with open(file_name, "r") as f:
                        output = f.read()
                        # Truncate to 1 KB
                        event_dict['output_txt'] = output[-1024:].replace('"', '\\"')
                else:
                    event_dict['output_txt'] = f'Output file not found in {file_name}'
            elif event_dict['event_name'] == "submit_end":
                file_name = os.path.join(event_dict['run_archive'], "submit.err")
                self.__logger.doDebugLogging(f"Using {file_name} for submit errors for Kafka")
                if os.path.exists(file_name):
                    with open(file_name, "r") as f:
                        output = f.read()
                        # Truncate to 1 KB
                        event_dict['output_txt'] = output[-1024:].replace('"', '\\"')
                else:
                    event_dict['output_txt'] = f'Output file not found in {file_name}'
            elif event_dict['event_name'] == "binary_execute_end":
                found_job_file = False
                for file_name in glob.glob(event_dict['run_archive'] + "/*.o" + event_dict['job_id']):
                    self.__logger.doDebugLogging(f"Using {file_name} for job output for Kafka")
                    if os.path.exists(file_name) and not found_job_file:
                        found_job_file = True
                        with open(file_name, "r") as f:
                            output = f.read()
                            # Truncate to 1 KB
                            event_dict['output_txt'] = output[-1024:].replace('"', '\\"')
                if not found_job_file:
                    event_dict['output_txt'] = f'Output file not found in {file_name}'
            elif event_dict['event_name'] == "check_end":
                file_name = os.path.join(event_dict['run_archive'], "output_check.txt")
                self.__logger.doDebugLogging(f"Using {file_name} for check output for Kafka")
                if os.path.exists(file_name):
                    with open(file_name, "r") as f:
                        output = f.read()
                        # Truncate to 1 KB
                        event_dict['output_txt'] = output[-1024:].replace('"', '\\"')
                else:
                    # if the update_databases wrapper calls this method, then it will provide an output_txt
                    event_dict['output_txt'] = f'Output file not found in {file_name}'
            else:
                # Even if event is not one with an output file, still log the output_txt column
                event_dict['output_txt'] = self.NO_VALUE

        # query_dict is a copy of event_dict, but holding only the information to send
        query_dict = {k: event_dict[k] if k in event_dict.keys() else self.NO_VALUE for k in self.KAFKA_EVENT_FIELDS}
        # Send message to Kafka & return the result True/False
        return self._send_message(self.topics['events'], query_dict)

    def send_metrics(self, test_info_dict : dict, metrics_dict : dict):
        """
            Posts metrics to Kafka.
        """
        if not 'metrics' in self.topics:
            self.__logger.doWarningLogging(f"The metrics topic is not initialized in Kafka logger {self.uri}. Skipping metrics logging.")
            return False

        self.__logger.doDebugLogging(f"Posting metrics from test id: {test_info_dict['test_id']} to Kafka")

        # pull info out of test_info_dict that we need & add metrics info
        query_dict = {k: test_info_dict[k] for k in self.KAFKA_COMMON_TEST_FIELDS} | metrics_dict

        # Send message to Kafka & return the result True/False
        return self._send_message(self.topics['metrics'], query_dict)

    def send_node_health_results(self, test_info_dict : dict, node_health_dict : dict):
        """
        Send node health data to Kafka
        """
        if not 'node_health' in self.topics:
            self.__logger.doWarningLogging(f"The node_health topic is not initialized in Kafka logger {self.uri}. Skipping node_health logging.")
            return False

        self.__logger.doDebugLogging(f"Posting node health data from test id: {test_info_dict['test_id']} to Kafka")

        # Required environment variable: RGT_NODE_LOCATION_FILE
        if not 'RGT_NODE_LOCATION_FILE' in os.environ:
            raise DatabaseEnvironmentError("RGT_NODE_LOCATION_FILE required to enable node health logging")

        # on frontier, xname encodes cabinet, chassis, rack, and board information (ie, complete location information)
        required_location_identifiers = ['xname']

        # find and read node location file -- json file
        use_node_location_file = True

        if 'RGT_NODE_LOCATION_FILE' in os.environ and str(os.environ['RGT_NODE_LOCATION_FILE']).lower() == 'none':
            use_node_location_file = False
        elif not 'RGT_NODE_LOCATION_FILE' in os.environ:
            # We want to abort in this case because previous runs may have been logged
            # with node location data, and we do not want to log incomplete data
            raise DatabaseEnvironmentError("The RGT_NODE_LOCATION_FILE environment variable is required. If you do not want this functionality, please set to \"None\".")
        else:
            # else, we assume it is a path and we look for it
            if not os.path.exists(os.environ['RGT_NODE_LOCATION_FILE']):
                raise DatabaseEnvironmentError(f"An RGT_NODE_LOCATION_FILE does not exist at {os.environ['RGT_NODE_LOCATION_FILE']}")

        node_locations = {}
        # Check if it's a file in valid JSON format -- if it fails, then the rgt_db_logger class will catch it
        if use_node_location_file:
            with open(f"{os.environ['RGT_NODE_LOCATION_FILE']}", 'r') as f:
                # if this generates an exception, it will be caught by parent class
                node_locations = json.loads(f.read())

        # for each node found in the nodecheck.txt
        for node_name in node_health_dict.keys():
            # Node health & test info
            query_dict = node_health_dict[node_name] | {k: test_info_dict[k] for k in self.KAFKA_COMMON_TEST_FIELDS}
            # Now add location info
            if node_name in node_locations.keys():
                for loc_id in required_location_identifiers:
                    if not loc_id in node_locations[node_name].keys():
                        self.__logger.doErrorLogging(f"Required location identifier {loc_id} not found for node {node_name}. Aborting node health logging.")
                    else:
                        query_dict[loc_id] = node_locations[node_name][loc_id]
            elif use_node_location_file:
                # If we were supposed to use a node location file, but couldn't find info for this node
                self.__logger.doErrorLogging(f"Could not find node location information for {node_name}. Aborting node health logging.")
                return False
            else:
                # still set these so that all records have consistent schema
                for loc_id in required_location_identifiers:
                    query_dict[loc_id] = self.NO_VALUE

            # Send message to Kafka
            ret = self._send_message(self.topics['node_health'], query_dict, synchronous=False)
            if not ret:
                # then flush the producer & exit
                self.producer.flush()
                self.__logger.doErrorLogging(f"Kafka message failed to send. Aborting node health logging.")
                return False
        # flush the producer to clear all messages
        self.producer.flush()

    def send_external_metrics(self, table : str, tags : dict, values : dict, log_time : str):
        """
            Posts external metrics to Kafka.
        """

        self.__logger.doDebugLogging(f"Posting external metrics to Kafka")

        # Add time to the query dictionary
        query_dict = tags | values
        query_dict['time'] = log_time

        # Send message to InfluxDB & return the result True/False
        return self._send_message(topic, query_dict)

    def is_alive(self):
        """
        Check if each of the provided topics exists in the Kafka instance
        """
        self.__logger.doDebugLogging(f'Checking for the following topics for Kafka health check and topic verification: {",".join(self.topics.values())} at {self.uri}')

        # requires broker v0.11 or later
        try:
            test_client = AdminClient(self.conf)
            for t in self.topics.keys():
                response = test_client.list_topics(topic=self.topics[t], timeout=10)
        except KafkaException as e:
            return f'A Kafka Exception occured while checking if the server is alive: {str(e)}'
        except Exception as e:
            return f'An Exception occured while checking if the server is alive: {str(e)}'

        return

    def query(self, query):
        """
        Parameters:
            query: a query string

        Returns:
            a list of dictionary objects
        """
        self.__logger.doCriticalLogging("The Kafka db_logger backend does not support the query() method yet. Support is planned for Druid via the RGT_KAFKA_DB_TYPE=Druid and RGT_KAFKA_DB_URI fields.")
        return []


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

    def _validate_uri(self):
        """
        Parses environment variables set for RGT_KAFKA_* and tests the connection
        """

        # The only Kafka variable that isn't parsed by the parent database handler is dryrun
        # All other fields are allowed to be semicolon-separated (for multiple instances),
        # so they must be parsed outside of here
        if self.kw['dryrun'] in os.environ and os.environ[self.kw['dryrun']] == '1':
            self.dryrun = True

        # Even though we don't set self.topics here, we can still check that it's non-empty
        # NOTE -- topics is not required to be length-3. If the metrics topic is not defined,
        # then it is disabled, and a warning will be printed
        if (len(self.topics) == 0):
            message = f'No Kafka topics could be found in the harness Kafka configurations.'
            raise DatabaseInitError(message)

    def _send_message(self, topic : str, payload : dict, synchronous : bool = True):
        """
        Sends the message to InfluxDB with the associated headers
        """

        if self.dryrun:
            self.__logger.doInfoLogging(f'Kafka dry-run is set via the {self.kw["dryrun"]} environment variable. Message: {payload}')
            return True
        elif self.kw['dryrun'] in os.environ and os.environ[self.kw['dryrun']] == '1':
            # A Harness utility may set the environment variable after DB init time
            self.dryrun = True
            self.__logger.doInfoLogging(f'Kafka dry-run is set via the {self.kw["dryrun"]} environment variable. Message: {payload}')
            return True

        self.__logger.doDebugLogging(f"Sending message to Kafka topic {topic}: {payload}")

        self.producer.produce(topic, value=json.dumps(payload))

        if synchronous:
            self.producer.flush()

    def _event_time_to_timestamp(self, event_time : str):
        """ Converts a time string to Unix timestamp in EST """

        # Check for different time formats
        if re.search(r"^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}\.[0-9]{6}$", event_time):
            # YYYY-MM-DDTHH:MM:SS.UUUUUU -- this is the default harness output
            log_time = datetime.strptime(event_time, "%Y-%m-%dT%H:%M:%S.%f")
        elif re.search(r"^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}\.[0-9]{6}Z$", event_time):
            # YYYY-MM-DDTHH:MM:SS.UUUUUUZ
            log_time = datetime.strptime(event_time, "%Y-%m-%dT%H:%M:%S.%fZ")
        elif re.search(r"^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}$", event_time):
            # YYYY-MM-DDTHH:MM:SS
            log_time = datetime.strptime(event_time, "%Y-%m-%dT%H:%M:%S")
        elif re.search(r"^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z$", event_time):
            # YYYY-MM-DDTHH:MM:SSZ
            log_time = datetime.strptime(event_time, "%Y-%m-%dT%H:%M:%S")
        else:
            raise DatabaseDataError(f"Unrecognized time format in string {event_time}.")

        if self.precision == "ms":
            return round(datetime.timestamp(log_time) * 1000 * 1000)
        else:
            return round(datetime.timestamp(log_time) * 1000 * 1000) * 1000
