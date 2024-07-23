#! /usr/bin/env python3

import os
from datetime import datetime
import requests
from urllib.parse import urlparse
from base_db import base_db

class influxdb_logger(base_db):

    """
    The logging class for InfluxDB databases
    """

    kw = {
        'uri': 'RGT_INFLUXDB_URI',
        'token': 'RGT_INFLUXDB_TOKEN',
        'bucket': 'RGT_INFLUXDB_BUCKET',
        'org': 'RGT_INFLUXDB_ORG',
        'precision': 'RGT_INFLUXDB_PRECISION'
    }

    #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
    #                                                                 @
    # Special methods                                                 @
    #                                                                 @
    #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

    def __init__(self,
                 uri='',
                 token='',
                 logger=None,
                 subtest=None):

        # This function can't be reached except through the parent
        # rgt_database_logger, which checks if the logger is not None
        self.logger = logger
        self.__subtest = subtest
        self.__full_uri = uri
        self.__token = token

        self.__url = None
        self.__bucket = None
        self.__org = None
        # Default of nanosecond precision
        self.__precision = 'ns'

        self._validate_uri()

        if not self.is_alive():
            message = f'An InfluxDB server at {self.__uri} is not alive'
            raise DatabaseInitError(message, {})

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

    def send_event(self, event_dict : dict):
        return

    def send_metrics(self, metrics_dict : dict):
        return

    def send_node_health_results(self, node_health_dict : dict):
        return

    def is_alive(self):
        # https://harness-influxdb-prod-stf016.apps.marble.ccs.ornl.gov/health

        return


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
        Parses the URI provided by RGT_INFLUXDB_URI
        Looks for bucket, organization, and precision specifiers
        Also strips the URI down to just the protocol & hostname
        """

        parsed = urlparse(self.__full_uri)
        # Check for a specified protocol (http, https)
        if len(parsed.scheme) == 0:
            message = f'The InfluxDB URI must specify the protocol (http, https, etc).'
            raise DatabaseInitError(message, {})
        # Get the raw URL for the InfluxDB server
        self.__url = f'{parsed.scheme}://{parsed.netloc}'
        for arg in parsed.query.split('&'):
            arg_split = arg.split('=')
            if arg_split[0] == 'bucket':
                self.__bucket = arg_split[1]
            elif arg_split[0] == 'org':
                self.__org = arg_split[1]
            elif arg_split[0] == 'precision':
                self.__precision = arg_split[1]
            else:
                message = f'Unrecognized URL-encoded keyword argument: {arg_split[0]}'
                raise DatabaseInitError(message, {})

        # Check if RGT_INFLUXDB_BUCKET, RGT_INFLUXDB_ORG, or
        # RGT_INFLUXDB_PRECISION are in the environment
        # These env-vars override what is in the RGT_INFLUXDB_URI
        if self.kw['bucket'] in os.environ:
            self.__bucket = os.environ[self.kw['bucket']]
        if self.kw['org'] in os.environ:
            self.__org = os.environ[self.kw['org']]
        if self.kw['precision'] in os.environ:
            self.__precision = os.environ[self.kw['precision']]

        if (not self.__bucket) or (not self.__org):
            message = f'The bucket and organization could not be found for the InfluxDB server.'
            message += f' The InfluxDB URI was {self.__full_uri}.'
            raise DatabaseInitError(message, {})
