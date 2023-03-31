#!/usr/bin/env python3

################################################################################
# Author: Nick Hagerty
# Date modified: 02-03-2023
################################################################################
# Purpose:
#   Provides a utility to log any data to InfluxDB for viewing in Grafana.
#   This submits data to a separate source from the harness metrics and events,
#   So the data will not become mixed.
################################################################################
# Requirements:
#   Must add a file named harness_keys.py that contains a dictionary named
#   influx_keys, containing key/value pairs (also dictionaries) in the format:
#       'instance_name': {
#           'POST': 'instance_token',
#           'token': 'instance_token'
#       }
#   where instance_name matches the argument of --db
################################################################################

import argparse
from datetime import datetime
import requests
import re
from harness_keys import influx_keys

# Initialize argparse ##########################################################
parser = argparse.ArgumentParser(description="Post a custom metric to InfluxDB")
parser.add_argument('--time', '-t', type=str, action='store', help="Timestamp to post record as. Format: YYYY-MM-DDTHH:MM:SS[.MS][Z]")
parser.add_argument('--keys', '-k', required=True, type=str, action='store', help="A set of comma-separated keys to identify your metric by. Ex: value_a=1,value_b=2")
parser.add_argument('--values', '-v', required=True, type=str, action='store', help="A set of comma-separated values to post. Ex: value_a=1,value_b=2. These may or may not be quoted")
parser.add_argument('--verbose', type=str, action='store', help="Increase verbosity.")
parser.add_argument('--table_name', default='non_harness_metrics', type=str, action='store', help="Specifies the name of the table (measurement) to post to.")
parser.add_argument('--db', required=True, type=str, action='store', help="Specifies the database to post metrics to.")
parser.add_argument('--nosend', action='store_true', help="When set, print the message to InfluxDB, but do not send.")

# Global URIs and Tokens #######################################################
try:
    from harness_keys import influx_keys
except:
    raise ImportError('Could not import harness_keys.py. Please make sure that you have a file named harness_keys.py in the search path. This is how this script reads information to query InfluxDB.')
################################################################################

# Parse command-line arguments #################################################
args = parser.parse_args()

# Set up URIs and Tokens #######################################################
if not args.db in influx_keys.keys():
    print(f"Unknown database version: {args.db} not found in influx_keys. Aborting.")
    exit(1)
elif not 'POST' in influx_keys[args.db]:
    print(f"POST URL not found in influx_keys[{args.db}]. Aborting.")
    exit(1)
elif not 'GET' in influx_keys[args.db]:
    print(f"GET URL not found in influx_keys[{args.db}]. Aborting.")
    exit(1)
elif not 'token' in influx_keys[args.db]:
    print(f"Influx token not found in influx_keys[{args.db}]. Aborting.")
    exit(1)

# Checking succeeded - global setup of URIs and tokens
post_influx_uri = influx_keys[args.db]['POST']
influx_token = influx_keys[args.db]['token']

headers = {
    'Authorization': f"Token {influx_token}",
    'Content-Type': "text/plain; charset=utf-8",
    'Accept': "application/json"
}

# Format check for keys & values ###############################################
def format_check(line):
    """ Format check for keys & values """
    # Expecting value_1=x,value_2=y
    splt_by_comma = line.split(',')
    for entry in splt_by_comma:
        splt_by_equal = entry.split('=')
        if not len(splt_by_equal) == 2:
            return [False, f'Invalid entry has more or less than 1 equal sign: {entry}']
        # Single quotes are not permitted in general
        if "'" in entry:
            return [False, f'Single quotes are not permitted in any keys/values: {entry}']
        # Check for unbalanced/ill-placed quotes
        if splt_by_equal[1].startswith('"') and not splt_by_equal[1].endswith('"'):
            return [False, f'Unbalanced quotes found in: {entry}']
        elif not splt_by_equal[1].startswith('"') and splt_by_equal[1].endswith('"'):
            return [False, f'Unbalanced quotes found in: {entry}']
        elif '"' in splt_by_equal[1][1:-1]:
            # If there's a quote in the middle of the string
            return [False, f'Quote found in the middle of a value: {entry}']
        # Check to make sure there's no quotes in the label
        if '"' in splt_by_equal[0]:
            return [False, f'Quotes not allowed in labels: {entry}']
    return [True, '']

ret = format_check(args.values)
if not ret[0]:
    print(f"Format check of values failed: {ret[1]}")
    exit(1)
ret = format_check(args.keys)
if not ret[0]:
    print(f"Format check of values failed: {ret[1]}")
    exit(1)

################################################################################

# Format check for time ########################################################
timestamp_ns = -1
if args.time:
    detected_time_fmt = False
    for fmt in ["%Y-%m-%dT%H:%M:%S", "%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%dT%H:%M:%S.%f", "%Y-%m-%dT%H:%M:%S.%fZ"]:
        try:
            log_time = datetime.strptime(args.time, fmt)
            timestamp_ns = int(datetime.timestamp(log_time) * 1000 * 1000) * 1000
            detected_time_fmt = True
            print(f"Found time in format of {fmt}")
            break
        except Exception as e:
            pass
################################################################################

# Format check for time ########################################################
number_regex = re.compile('^([0-9]*\.)?[0-9]+(e[+-]?[0-9]+)?$')
values_formatted = []
for val in args.values.split(','):
    # We know it's properly formatted already
    val_splt = val.split('=')
    # We know quotes are balanced - if the starting quote is there, so is end
    if not val_splt[1].startswith('"'):
        if not number_regex.match(val_splt[1]):
            val_splt[1] = '"' + val_splt[1] + '"'
        # else, it's a valid decimal number
    elif val_splt[1].startswith('"') and number_regex.match(val_splt[1][1:-1]):
        # If it's a number, un-quote it (otherwise InfluxDB thinks it's a str)
        val_splt[1] = val_splt[1][1:-1]
    values_formatted.append(f'{val_splt[0]}={val_splt[1]}')

################################################################################

# Package & send ###############################################################
influx_post_str = f"{args.table_name},{args.keys}"
influx_post_str += f" {','.join(values_formatted)}"
if args.time:
    influx_post_str += f" {timestamp_ns}"
try:
    if args.nosend:
        print(f"NOSEND set: {influx_post_str}")
        exit(0)
    r = requests.post(post_influx_uri, data=influx_post_str, headers=headers)
    if int(r.status_code) < 400:
        print(f"Successfully sent {influx_post_str} to {post_influx_uri}")
    else:
        print(f"Influx returned status code: {r.status_code} in response to data: {influx_post_str}")
        print(r.text)
        exit(1)
    exit(0)
except requests.exceptions.ConnectionError as e:
    print("InfluxDB is not reachable. Request not sent.")
    exit(1)
except Exception as e:
    print(f"Failed to send {influx_event_record_string} to {self.influx_url}:")
exit(2)
################################################################################
