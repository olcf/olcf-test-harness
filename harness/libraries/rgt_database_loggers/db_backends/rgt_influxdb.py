#! /usr/bin/env python3

import csv
from datetime import datetime
import glob
import json
import os
import re
import requests
from urllib.parse import urlparse

from libraries.rgt_database_loggers.db_backends.base_db import *

class InfluxDBLogger(BaseDBLogger):

    """
    The logging class for InfluxDB databases
    """

    kw = {
        'uri': 'RGT_INFLUXDB_URI',
        'token': 'RGT_INFLUXDB_TOKEN',
        'bucket': 'RGT_INFLUXDB_BUCKET',
        'org': 'RGT_INFLUXDB_ORG',
        'precision': 'RGT_INFLUXDB_PRECISION',
        'dryrun': 'RGT_INFLUXDB_DRY_RUN',
        'disable': 'RGT_INFLUXDB_DISABLE'
    }

    # Re-defines the StatusFile.NOVALUE
    NO_VALUE = '[NO_VALUE]'

    #---Influx key identifiers.
    INFLUX_TAGS = [
                'test_id',
                'app',
                'test',
                'runtag',
                'machine'
    ]

    # Excludes test_instance, since that is comma-separated values derived from other fields
    INFLUX_EVENT_FIELDS = [
                'build_directory',
                'event_filename',
                'event_name',
                'event_subtype',
                'event_time',
                'event_type',
                'event_value',
                'check_alias',
                'hostname',
                'job_account_id',
                'job_id',
                'path_to_rgt_package',
                'rgt_path_to_sspace',
                'rgt_system_log_tag',
                'run_archive',
                'user',
                'workdir',
                'comment',
                'output_txt'
    ]

    DISABLE_DOTFILE_NAME = '.disable_influxdb'
    SUCCESSFUL_DOTFILE_NAME = '.success_influxdb'

    #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
    #                                                                 @
    # Special methods                                                 @
    #                                                                 @
    #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

    def __init__(self,
                 uri='',
                 token='',
                 logger=None):

        # This function can't be reached except through the parent
        # rgt_database_logger, which checks if the logger is not None
        self.__logger = logger
        self.full_uri = uri
        self.token = token

        self.url = None
        self.bucket = None
        self.org = None
        # Default of nanosecond precision
        self.precision = 'ns'
        self.dryrun = False

        self._validate_uri()

        alive_msg = self.is_alive()
        if alive_msg:
            message = f'An InfluxDB server at {self.url} is not alive: {alive_msg}'
            raise DatabaseInitError(message)

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
        return 'influxdb'

    def send_event(self, event_dict : dict):
        """
            Posts the event to InfluxDB.
        """
        self.__logger.doDebugLogging(f"Posting event {event_dict['event_name']} for test id: {event_dict['test_id']} to Influx")

        # Initialize the tags for record string
        influx_event_record_string = 'events'

        # Check that required tags exist
        for tag_name in self.INFLUX_TAGS:
            if not tag_name in event_dict.keys():
                message = "Could not find required InfluxDB tag in event dictionary: {tag_name}"
                raise DatabaseDataError(message)
            influx_event_record_string += f',{tag_name}={event_dict[tag_name]}'

        # Add fields to influx record string
        # First field separated by space, every other field by commas
        sep=' '
        for field_name in self.INFLUX_EVENT_FIELDS:
            if field_name == 'output_txt':
                # don't add output_txt yet
                continue
            elif not field_name in event_dict.keys():
                # We don't expect the comment to be populated yet.
                if not field_name == 'comment':
                    self.__logger.doWarningLogging(f"Couldn't find InfluxDB field: {field_name}. Setting to NOVALUE")
                event_dict[field_name] = self.NO_VALUE
            influx_event_record_string += f'{sep}{field_name}="{event_dict[field_name]}"'
            sep = ','

        if not 'output_txt' in event_dict.keys():
            # Add handling for pasting outputs to influxdb
            if event_dict['event_name'] == "build_end":
                file_name = os.path.join(event_dict['build_directory'], "output_build.txt")
                self.__logger.doDebugLogging(f"Using {file_name} for build output for Influx")
                if os.path.exists(file_name):
                    with open(file_name, "r") as f:
                        output = f.read()
                        # Truncate to 64 kb
                        output = output[-65534:].replace('"', '\\"')
                        influx_event_record_string += ",output_txt=\"" + output + "\""
                else:
                    influx_event_record_string += ",output_txt=\"Output file not found in " + file_name  + "\""
            elif event_dict['event_name'] == "submit_end":
                file_name = os.path.join(event_dict['run_archive'], "submit.err")
                self.__logger.doDebugLogging(f"Using {file_name} for submit errors for Influx")
                if os.path.exists(file_name):
                    with open(file_name, "r") as f:
                        output = f.read()
                        # Truncate to 64 kb
                        output = output[-65534:].replace('"', '\\"')
                        influx_event_record_string += ",output_txt=\"" + output + "\""
                else:
                    influx_event_record_string += ",output_txt=\"Output file not found in " + file_name + "\""
            elif event_dict['event_name'] == "binary_execute_end":
                found_job_file = False
                for file_name in glob.glob(event_dict['run_archive'] + "/*.o" + event_dict['job_id']):
                    self.__logger.doDebugLogging(f"Using {file_name} for job output for Influx")
                    if os.path.exists(file_name):
                        found_job_file = True
                        with open(file_name, "r") as f:
                            output = f.read()
                            # Truncate to 64 kb
                            output = output[-65534:].replace('"', '\\"')
                            influx_event_record_string += ",output_txt=\"" + output + "\""
                if not found_job_file:
                    influx_event_record_string += ",output_txt=\"Job output file not found" + "\""
            elif event_dict['event_name'] == "check_end":
                file_name = os.path.join(event_dict['run_archive'], "output_check.txt")
                self.__logger.doDebugLogging(f"Using {file_name} for check output for Influx")
                if os.path.exists(file_name):
                    with open(file_name, "r") as f:
                        output = f.read()
                        # Truncate to 64 kb
                        output = output[-65534:].replace('"', '\\"')
                        influx_event_record_string += ",output_txt=\"" + output + "\""
                else:
                    # if the update_databases wrapper calls this method, then it will provide an output_txt
                    influx_event_record_string += ",output_txt=\"Output file not found in " + file_name + "\""
            else:
                # Even if event is not one with an output file, still log the output_txt metric
                influx_event_record_string += ",output_txt=\"" + self.NO_VALUE  + "\""
        else:
            influx_event_record_string += ",output_txt=\"" + event_dict['output_txt'] + "\""
                

        influx_event_record_string += f" {str(self._event_time_to_timestamp(event_dict['event_time']))}"

        headers = {'Authorization': f'Token {self.token}', 'Content-Type': "text/plain; charset=utf-8", 'Accept': "application/json"}

        # Send message to InfluxDB & return the result True/False
        return self._send_message(self._get_write_url(), influx_event_record_string, headers)

    def send_metrics(self, test_info_dict : dict, metrics_dict : dict):
        """
            Posts metrics to InfluxDB.
        """
        self.__logger.doDebugLogging(f"Posting metrics from test id: {test_info_dict['test_id']} to InfluxDB")

        # Initialize the tags for record string
        influx_event_record_string = 'metrics'

        # Check that required tags exist
        for tag_name in self.INFLUX_TAGS:
            if not tag_name in test_info_dict.keys():
                message = "Could not find required InfluxDB tag in metrics dictionary: {tag_name}"
                raise DatabaseDataError(message)
            influx_event_record_string += f',{tag_name}={test_info_dict[tag_name]}'

        influx_event_record_string += ' '
        influx_event_record_string += ','.join([f"{k}={v}" for k, v in metrics_dict.items()])
        influx_event_record_string += f" {str(self._event_time_to_timestamp(test_info_dict['event_time']))}"

        headers = {'Authorization': f'Token {self.token}', 'Content-Type': "text/plain; charset=utf-8", 'Accept': "application/json"}

        # Send message to InfluxDB & return the result True/False
        return self._send_message(self._get_write_url(), influx_event_record_string, headers)

    def send_node_health_results(self, test_info_dict : dict, node_health_dict : dict):
        """
        Send node health data to InfluxDB
        """
        self.__logger.doDebugLogging(f"Posting node health data from test id: {test_info_dict['test_id']} to InfluxDB")
        # Required environment variable: RGT_NODE_LOCATION_FILE
        if not 'RGT_NODE_LOCATION_FILE' in os.environ:
            raise DatabaseEnvironmentError("RGT_NODE_LOCATION_FILE required to enable node health logging")

        required_tags = ['test', 'machine', 'test_id', 'event_time']

        # Check that test_info_dict provided all required tags
        for t in required_tags:
            if not t in test_info_dict.keys():
                raise DatabaseDataError(f"Test info provided to node health logging missing tag: {t}")

        influxdb_tags = ['test', 'machine']
        static_tag_line = ','.join([f'{k}={test_info_dict[k]}' for k in influxdb_tags])

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
        # By default, we don't want to log node healths without extra node location (like cabinet, chassis, etc)
        # check if it's a file in valid JSON format
        # each entry is node_name: { 'status': 'FAILED'|'SUCCESS', 'message': '' }
        json_read_success = True
        if use_node_location_file:
            import json
            with open(f"{os.environ['RGT_NODE_LOCATION_FILE']}", 'r') as f:
                # if this generates an exception, it will be caught by parent class
                node_locations = json.loads(f.read())
        # collect all node health lines, then post in one single batch
        post_lines = []
        # for each node found in the nodecheck.txt
        for node_name in node_health_dict.keys():
            influx_event_record_string = f'node_health,{static_tag_line},node={node_name}'
            if node_name in node_locations.keys():
                # then it's a node location identifier
                for k in node_locations[node_name].keys():
                    influx_event_record_string += f',{k}={node_locations[node_name][k]}'
            node_data_string = ','.join([f'{k}="{v}"' for k,v in node_health_dict[node_name].items()])
            influx_event_record_string += f' test_id="{test_info_dict["test_id"]}",{node_data_string}'
            influx_event_record_string += f" {str(self._event_time_to_timestamp(test_info_dict['event_time']))}"
            post_lines.append(influx_event_record_string)

        headers = {'Authorization': f'Token {self.token}', 'Content-Type': "text/plain; charset=utf-8", 'Accept': "application/json"}
        # Send message to InfluxDB & return the True/False result
        return self._send_message(self._get_write_url(), '\n'.join(post_lines), headers)

    def send_external_metrics(self, table : str, tags : dict, values : dict, log_time : str):
        """
            Posts external metrics to InfluxDB.
        """
        self.__logger.doDebugLogging(f"Posting external metrics to InfluxDB")

        # Initialize the tags for record string
        influx_event_record_string = table

        # Check that required tags exist
        for tag_name in tags.keys():
            influx_event_record_string += f',{tag_name}={tags[tag_name]}'

        influx_event_record_string += ' '
        influx_event_record_string += ','.join([f"{k}={v}" for k, v in values.items()])
        influx_event_record_string += f" {str(self._event_time_to_timestamp(log_time))}"

        headers = {'Authorization': f'Token {self.token}', 'Content-Type': "text/plain; charset=utf-8", 'Accept': "application/json"}

        # Send message to InfluxDB & return the result True/False
        return self._send_message(self._get_write_url(), influx_event_record_string, headers)

    def is_alive(self):
        """
        Query the /api/v2/buckets endpoint of the InfluxDB server to check for the specified bucket.
        """
        headers = {
            'Authorization': f'Token {self.token}',
            'Content-Type': "application/json",
            'Accept': "application/json"
        }

        self.__logger.doDebugLogging(f'Using the following endpoint for InfluxDB health check and bucket verification: {self.url}/api/v2/buckets')
        r = requests.get(f'{self.url}/api/v2/buckets', headers=headers)
        if int(r.status_code) >= 400:
            return f"status_code = {r.status_code}, text = {r.text}, reason = {r.reason}"
        json_success = False
        try:
            resp = r.json()
            json_success = True
        except Exception as e:
            pass
        if not json_success:
            return f"JSON response in is_alive() failed to parse."
        if not 'buckets' in resp:
            return f"no buckets found in the InfluxDB instance"
        found_bucket = False
        for b in resp['buckets']:
            if b['name'] == self.bucket:
                found_bucket = True

        if not found_bucket:
            return f"could not find bucket {self.bucket}"

        return

    def query(self, query):
        """
        Query the /api/v2/read endpoint of the InfluxDB server to check for the specified bucket.

        Parameters:
            query: a Flux-formatted query string

        Returns:
            a list of dictionary objects
        """
        headers = {
            'Authorization': f'Token {self.token}',
            'Content-Type': "application/vnd.flux",
            'Accept': "application/json"
        }

        self.__logger.doDebugLogging(f'Sending query: {query} to: {self.url}/api/v2/query')
        r = requests.post(f'{self.url}/api/v2/query?org={self.org}', data=query, headers=headers)
        if int(r.status_code) >= 400:
            self.__logger.doErrorLogging(f"InfluxDB request failed. status_code = {r.status_code}, text = {r.text}, reason = {r.reason}")
            return []
        rdc = r.content.decode('utf-8')
        resp = list(csv.reader(rdc.splitlines(), delimiter=','))
        # each entry in series is a record
        col_names = resp[0]
        # Transforming into list of dictionaries
        ret_data = []
        for entry_index in range(1, len(resp)):
            data_tmp = {}
            if len(resp[entry_index]) == 0:
                # Empty row, usually just a spacing formality
                continue
            if len(resp[entry_index]) < len(col_names):
                self.__logger.doErrorLogging(f"Not enough columns in row. Skipping row: {resp[entry_index]}.")
                continue
            # First column is useless
            for c_index in range(1, len(col_names)):
                # Ignore result, table & _time
                if not col_names[c_index] in ["result", "table", "_time"]:
                    data_tmp[col_names[c_index]] = resp[entry_index][c_index]
            ret_data.append(data_tmp)
        return ret_data


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

    def _get_write_url(self):
        """
        Construct the URL for the Write API endpoint
        """
        return f'{self.url}/api/v2/write?org={self.org}&bucket={self.bucket}&precision={self.precision}'

    def _validate_uri(self):
        """
        Parses the URI provided by RGT_INFLUXDB_URI
        Looks for bucket, organization, and precision specifiers
        Also strips the URI down to just the protocol & hostname
        """

        parsed = urlparse(self.full_uri)
        # Check for a specified protocol (http, https)
        if len(parsed.scheme) == 0:
            message = f'The InfluxDB URI must specify the protocol (http, https, etc).'
            raise DatabaseInitError(message)
        # Get the raw URL for the InfluxDB server
        self.url = f'{parsed.scheme}://{parsed.netloc}'
        for arg in parsed.query.split('&'):
            arg_split = arg.split('=')
            if arg_split[0] == 'bucket':
                self.bucket = arg_split[1]
            elif arg_split[0] == 'org':
                self.org = arg_split[1]
            elif arg_split[0] == 'precision':
                self.precision = arg_split[1]
            else:
                message = f'Unrecognized URL-encoded keyword argument: {arg_split[0]}'
                raise DatabaseInitError(message)

        # Check if RGT_INFLUXDB_BUCKET, RGT_INFLUXDB_ORG, or
        # RGT_INFLUXDB_PRECISION are in the environment
        # These env-vars override what is in the RGT_INFLUXDB_URI
        if self.kw['bucket'] in os.environ:
            self.bucket = os.environ[self.kw['bucket']]
        if self.kw['org'] in os.environ:
            self.org = os.environ[self.kw['org']]
        if self.kw['precision'] in os.environ:
            self.precision = os.environ[self.kw['precision']]
        if self.kw['dryrun'] in os.environ and os.environ[self.kw['dryrun']] == '1':
            self.dryrun = True

        if (not self.bucket) or (not self.org):
            message = f'The bucket and organization for the InfluxDB server could not be found.'
            message += f' The InfluxDB URI was {self.full_uri}.'
            raise DatabaseInitError(message)

    def _send_message(self, full_url : str, message : str, headers : dict):
        """
        Sends the message to InfluxDB with the associated headers
        """

        if self.dryrun:
            self.__logger.doInfoLogging(f'InfluxDB dry-run is set via the {self.kw["dryrun"]} environment variable. Message: {message}')
            return True
        elif self.kw['dryrun'] in os.environ and os.environ[self.kw['dryrun']] == '1':
            # A Harness utility may set the environment variable after DB init time
            self.dryrun = True
            self.__logger.doInfoLogging(f'InfluxDB dry-run is set via the {self.kw["dryrun"]} environment variable. Message: {message}')
            return True

        self.__logger.doDebugLogging(f"Sending message to InfluxDB: {message}")
        # We do not catch the exception here -- it will be caught in the database manager class
        r = requests.post(full_url, data=message.encode('utf-8'), headers=headers)

        if r.status_code == 200 or r.status_code == 204:
            self.__logger.doDebugLogging(f"Logged to InfluxDB successfully ({r.status_code}, {r.reason}): {message}")
            return True
        else:
            self.__logger.doErrorLogging(f"Failed to post to InfluxDB. Message: {message}, Response: {r.status_code} - {r.reason}")
            return False

    def _event_time_to_timestamp(self, event_time : str):
        """ Converts a time string to Unix timestamp in EST """

        # Check for different time formats
        if re.search("^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}\.[0-9]{6}$", event_time):
            # YYYY-MM-DDTHH:MM:SS.UUUUUU -- this is the default harness output
            log_time = datetime.strptime(event_time, "%Y-%m-%dT%H:%M:%S.%f")
        elif re.search("^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}\.[0-9]{6}Z$", event_time):
            # YYYY-MM-DDTHH:MM:SS.UUUUUUZ
            log_time = datetime.strptime(event_time, "%Y-%m-%dT%H:%M:%S.%fZ")
        elif re.search("^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}$", event_time):
            # YYYY-MM-DDTHH:MM:SS
            log_time = datetime.strptime(event_time, "%Y-%m-%dT%H:%M:%S")
        elif re.search("^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z$", event_time):
            # YYYY-MM-DDTHH:MM:SSZ
            log_time = datetime.strptime(event_time, "%Y-%m-%dT%H:%M:%S")
        else:
            raise DatabaseDataError(f"Unrecognized time format in string {event_time}.")

        if self.precision == "ms":
            return round(datetime.timestamp(log_time) * 1000 * 1000)
        else:
            return round(datetime.timestamp(log_time) * 1000 * 1000) * 1000
