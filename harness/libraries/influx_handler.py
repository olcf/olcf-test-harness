#!/usr/bin/env python3
#
# Author: Nick Hagerty (hagertynl@ornl.gov)
# National Center for Computational Sciences, System Acceptance & User Environment Group
# Oak Ridge National Laboratory
#

# Python package imports
import sys
# Requests should be a non-fatal error
try:
    import requests
except ImportError as e:
    print("Import Warning: Could not import requests in current Python environment. Influx logging will be disabled.")

class influx_handler:
    """
        Abstracts the handling of InfluxDB requests
    """
    #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
    #                                                                 @
    # Special methods                                                 @
    #                                                                 @
    #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

    def __init__(self, logger=None):
        # Inherit logger from the class that initializes this class
        self.logger = logger

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

    def post(self, msg):
        """
            Posts an event to InfluxDB
        """
        # Check if InfluxDB is explicitly disabled:
        if 'RGT_DISABLE_INFLUX' in os.environ and str(os.environ['RGT_DISABLE_INFLUX']) == '1':
            self.logger.doInfoLogging("InfluxDB is explicitly disabled with RGT_DISABLE_INFLUX=1")
            return False
        # Required environment variables:
        if not ('RGT_INFLUX_URI' in os.environ and 'RGT_INFLUX_TOKEN' in os.environ):
            # Then we don't know where/how to post
            self.logger.doWarningLogging('RGT_INFLUX_URI and RGT_INFLUX_TOKEN are required environment variables to enable InfluxDB logging')
            return False
        # Failed import of requests is non-fatal, since InfluxDB is an extension. Check to make sure it imported
        if not 'requests' in sys.modules:
            self.logger.doWarningLogging(f"'requests' is not in sys.modules. InfluxDB logging is disabled. Events can be logged after the run using --mode influx_log.")
            self.logger.doInfoLogging(f"Skipping message: {msg}.")
            return False
        # These headers are common for all post requests
        headers = {
            'Authorization': f"Token {os.environ['RGT_INFLUX_TOKEN']}",
            'Content-Type': "text/plain; charset=utf-8",
            'Accept': "application/json"
        }
        # Try to POST
        try:
            influx_url = os.environ['RGT_INFLUX_URI']
            if 'RGT_INFLUX_NO_SEND' in os.environ and os.environ['RGT_INFLUX_NO_SEND'] == '1':
                print(f"RGT_INFLUX_NO_SEND is set, echoing: {msg}")
            else:
                r = requests.post(influx_url, data=msg, headers=headers)
                # Any status code < 400 is successful
                if not int(r.status_code) < 400:
                    self.logger.doWarningLogging(f"Influx returned status code: {r.status_code}")
                    return False
            self.logger.doInfoLogging(f"Successfully sent {msg} to {influx_url}")
        except requests.exceptions.ConnectionError as e:
            self.logger.doWarningLogging(f"InfluxDB is not reachable. Request not sent: {msg}")
            return False
        except Exception as e:
            # TODO: add more graceful handling of unreachable influx servers
            self.logger.doErrorLogging(f"Failed to send {msg} to {influx_url}:")
            self.logger.doErrorLogging(e)
            return False
        return True

    def query_flux(self, query, url=None):
        """
            Sends Flux query to InfluxDB URL
            url is an optional parameter to specify the URL for InfluxDB.
            If url is not provided, this script will attempt to replace the url path
            of os.environ['RGT_INFLUX_URI']
        """
        return []

    #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
    #                                                                 @
    # End of public methods.                                          @
    #                                                                 @
    #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

    #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
    #                                                                 @
    # Private methods                                                 @
    #                                                                 @
    #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

    def _parse_query_result_from_csv(self, resp):
        """
            Parse query results from the annotated CSV format. Typically from Flux queries.
            Automatically excludes _measurement, _result, _start, _stop
        """
        return []

    #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
    #                                                                 @
    # End of private methods                                          @
    #                                                                 @
    #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
