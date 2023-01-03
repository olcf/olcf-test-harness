#!/usr/bin/env python3
#
# Author: Nick Hagerty (hagertynl@ornl.gov)
# National Center for Computational Sciences, System Acceptance & User Environment Group
# Oak Ridge National Laboratory
#

# Python package imports
import sys
import os
import csv
from urllib.parse import urlparse, quote

# Requests should be a non-fatal error
try:
    import requests
except ImportError as e:
    print("Import Warning: Could not import requests in current Python environment. Influx logging will be disabled.")

# When this script is run by a utility, the rgt_logger class may not be initialized by default
class default_logger:
    def __init__(self):
        pass

    def write_msg(self, label, msg):
        print(f"[{label}] {msg}")

    def doInfoLogging(self, msg):
        self.write_msg('INFO', msg)

    def doWarningLogging(self, msg):
        self.write_msg('INFO', msg)

    def doErrorLogging(self, msg):
        self.write_msg('INFO', msg)


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
        if not logger:
            print("logger parameter not provided to influx_handler. Defaulting to stdout")
            self.logger = default_logger()
        else:
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

    def query_flux(self, query, url=None, token=None):
        """
            Sends Flux query to InfluxDB URL
            url is an optional parameter to specify the URL for InfluxDB.
            If url is not provided, this script will attempt to replace the url path
            of os.environ['RGT_INFLUX_URI']
            If token is not provided, this script will use os.environ['RGT_INFLUX_TOKEN']
        """
        # Failed import of requests is non-fatal, since InfluxDB is an extension. Check to make sure it imported
        if not 'requests' in sys.modules:
            self.logger.doWarningLogging(f"'requests' is not in sys.modules. InfluxDB logging is disabled. Events can be logged after the run using --mode influx_log.")
            self.logger.doInfoLogging(f"Skipping message: {msg}.")
            return False
        # Check if we have the URI and token required to post
        if not (('RGT_INFLUX_URI' in os.environ or url) and ('RGT_INFLUX_TOKEN' in os.environ or token)):
            # Then we don't know where/how to post
            self.logger.doWarningLogging('RGT_INFLUX_URI and RGT_INFLUX_TOKEN are required environment variables to enable InfluxDB logging, \
                                            or the url and token parameters must be specified')
            return False
        influx_url = url if url else os.environ['RGT_INFLUX_URI']
        # Checks to make sure the URL is properly formatted
        influx_url = self._check_url_endpoint(influx_url)
        influx_token = token if token else os.environ['RGT_INFLUX_TOKEN']
        # These headers are common for all post requests
        headers = {
            'Authorization': f"Token {influx_token}",
            'Content-type': 'application/vnd.flux',
            'Accept': "application/json"
        }
        # Check if endpoint is a `/api/v2/write?...` match. If it is, replace /api/v2/write with /api/v2/query
        self.logger.doInfoLogging(f"Running: {query} on {influx_url}")
        try:
            r = requests.post(influx_url, headers=headers, data=query)
            if int(r.status_code) >= 400:
                self.logger.doWarningLogging(f"Influx request failed, status_code = {r.status_code}, text = {r.text}, reason = {r.reason}.")
                return []
        except requests.exceptions.ConnectionError as e:
            self.logger.doErrorLogging("InfluxDB is not reachable. Request not sent.")
            self.logger.doErrorLogging(str(e))
            return []
        except Exception as e:
            self.logger.doErrorLogging(f"Failed to send to {influx_url}:")
            self.logger.doErrorLogging(str(e))
            return []
        rdc = r.content.decode('utf-8')
        resp = list(csv.reader(rdc.splitlines(), delimiter=','))
        ret_data = self._parse_query_result_from_csv(resp)
        return ret_data

    def query_influxql(self, query, url=None, token=None):
        """
            Sends InfluxQL query to InfluxDB URL
            url is an optional parameter to specify the URL for InfluxDB.
            If url is not provided, this script will attempt to replace the url path
            of os.environ['RGT_INFLUX_URI']
            If token is not provided, this script will use os.environ['RGT_INFLUX_TOKEN']
        """
        # Failed import of requests is non-fatal, since InfluxDB is an extension. Check to make sure it imported
        if not 'requests' in sys.modules:
            self.logger.doWarningLogging(f"'requests' is not in sys.modules. InfluxDB logging is disabled. Events can be logged after the run using --mode influx_log.")
            self.logger.doInfoLogging(f"Skipping message: {msg}.")
            return False
        # Check if we have the URI and token required to post
        if not (('RGT_INFLUX_URI' in os.environ or url) and ('RGT_INFLUX_TOKEN' in os.environ or token)):
            # Then we don't know where/how to post
            self.logger.doWarningLogging('RGT_INFLUX_URI and RGT_INFLUX_TOKEN are required environment variables to enable InfluxDB logging, \
                                            or the url and token parameters must be specified')
            return False
        influx_url = url if url else os.environ['RGT_INFLUX_URI']
        # Checks to make sure the URL is properly formatted
        influx_url = self._check_url_endpoint(influx_url, v2_api=False)
        influx_token = token if token else os.environ['RGT_INFLUX_TOKEN']
        # These headers are common for all post requests
        headers = {
            'Authorization': f"Token {influx_token}",
            'Accept': "application/json"
        }
        if '?' in influx_url:
            url_with_query = f"{influx_url}&q={quote(query)}"
        else:
            url_with_query = f"{influx_url}?q={quote(query)}"
        self.logger.doInfoLogging(f"Running: {query} on {influx_url}")
        try:
            r = requests.get(url_with_query, headers=headers)
            if int(r.status_code) >= 400:
                self.logger.doWarningLogging(f"Influx request failed, status_code = {r.status_code}, text = {r.text}, reason = {r.reason}.")
                return []
        except requests.exceptions.ConnectionError as e:
            self.logger.doErrorLogging("InfluxDB is not reachable. Request not sent.")
            self.logger.doErrorLogging(str(e))
            return []
        except Exception as e:
            self.logger.doErrorLogging(f"Failed to send to {influx_url}:")
            self.logger.doErrorLogging(str(e))
            return []
        resp = r.json()
        ret_data = self._parse_query_result_from_json(resp)
        return ret_data

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

    def _check_url_endpoint(self, url, read=True, v2_api=True):
        """
            Checks the endpoint of the URL
        """
        url_parsed = urlparse(url)
        endpoint = url_parsed.path
        target_endpoint = endpoint
        if read and v2_api:
            # Then the endpoint should be /api/v2/query?org=accept
            if not endpoint.startswith('/api/v2/query'):
                target_endpoint = f'/api/v2/query'
                self.logger.doWarningLogging(f'Found bad endpoint for v2 read request. Got: {endpoint}, expected {target_endpoint}.')
        elif read and (not v2_api):
            # Then the endpoint should be /query?org=accept
            if not endpoint.startswith('/query'):
                target_endpoint = f'/query'
                self.logger.doWarningLogging(f'Found bad endpoint for v1 read request. Got: {endpoint}, expected {target_endpoint}.')
        elif not read:
            # All write queries have the same endpoint -- /api/v2/write
            if not endpoint.startswith('/api/v2/write'):
                target_endpoint = f'/api/v2/write'
                self.logger.doWarningLogging(f'Found bad endpoint for v2 write request. Got: {endpoint}, expected {target_endpoint}.')
        return url_parsed._replace(path=target_endpoint).geturl()

    def _parse_query_result_from_csv(self, resp):
        """
            Parse query results from the annotated CSV format. Typically from Flux queries.
            Automatically excludes _measurement, _result, _start, _stop
        """
        if len(resp) == 0:
            self.logger.doWarningLogging("Query result has no content")
            return []
        ret_data = []
        # each entry in nested list is a record
        col_names = resp[0]
        for entry_index in range(1, len(resp)):
            data_tmp = {}
            if len(resp[entry_index]) < len(col_names):
                self.logger.doInfoLogging(f"Row does not have enough fields to match column names. Skipping row: {resp[entry_index]}.")
                continue
            # First column is useless
            for c_index in range(1, len(col_names)):
                # Ignore result, table & rename time
                if col_names[c_index] == "_time":
                    data_tmp["time"] = resp[entry_index][c_index]
                elif not (col_names[c_index] == "result" or col_names[c_index] == "table" or col_names[c_index].startswith('_')):
                    data_tmp[col_names[c_index]] = resp[entry_index][c_index]
            ret_data.append(data_tmp)
        return ret_data

    def _parse_query_result_from_json(self, resp):
        """
            Parse query results from the JSON format. Typically from InfluxQL queries.
        """
        # Check nested structure to ensure there's responses
        if (not 'results' in resp) or (len(resp['results']) == 0) or (not 'series' in resp['results'][0]):
            self.logger.doWarningLogging("Query result has no content")
            return []
        ret_data = []
        # each entry in nested list is a record
        for series in range(0, len(resp['results'][0]['series'])):
            col_names = resp['results'][0]['series'][series]['columns']
            values = resp['results'][0]['series'][series]['values']
            if 'tags' in resp['results'][0]['series'][series]:
                tags_d = resp['results'][0]['series'][series]['tags']
                tag_line = ','.join([f"{k}={v}" for k, v in tags_d.items()])
            else:
                tag_line = ''
            # Let's do the work of transforming this into a list of dicts
            for entry_index in range(0, len(values)):
                data_tmp = {}
                if len(tag_line) > 1:
                    data_tmp['tags'] = tag_line
                for c_index in range(0, len(col_names)):
                    data_tmp[col_names[c_index]] = values[entry_index][c_index]
                ret_data.append(data_tmp)
        return ret_data

    #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
    #                                                                 @
    # End of private methods                                          @
    #                                                                 @
    #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
