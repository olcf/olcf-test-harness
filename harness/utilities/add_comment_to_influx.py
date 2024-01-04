#!/usr/bin/env python3

################################################################################
# Author: Nick Hagerty
# Date modified: 11-29-2022
################################################################################
# Purpose:
#   Allows users to add comments to a specific event (ie, build_start) of
#   harness jobs in InfluxDB. Logs event back to influx with same timestamp.
################################################################################
# Requirements:
#   Requires a file named harness_keys.py which contains the post_influx_uri,
#   get_influx_uri, influx_token for the targeted InfluxDB instance.
################################################################################

import os
import sys
import requests
import subprocess
import urllib.parse
import datetime
import argparse

try:
    from status_file import StatusFile
except:
    raise ImportError('Could not import status_file.py. Please make sure the olcf_harness module is loaded.')



# Initialize argparse ##########################################################
parser = argparse.ArgumentParser(description="Updates harness run in InfluxDB with a comment")
parser.add_argument('--testid', '-t', type=str, action='store', required=True, help="Specifies the harness test id to update jobs for.")
parser.add_argument('--message', '-m', type=str, action='store', required=True, help="Comment to add to the record.")
parser.add_argument('--db', type=str, required=True, action='store', help="InfluxDB instance name to log to.")
parser.add_argument('--event', type=str, action='store', choices=['logging_start', 'build_start', 'build_end', 'submit_start', \
                        'submit_end', 'job_queued', 'binary_execute_start', 'binary_execute_end', 'check_start', 'check_end'], \
                        help="Specifies the harness event to add the comment to.")
################################################################################

# Global URIs and Tokens #######################################################
from harness_keys import influx_keys
################################################################################

# Parse command-line arguments #################################################
args = parser.parse_args()  # event field already validated by 'choices'

# Set up URIs and Tokens #######################################################
if not args.db in influx_keys.keys():
    print(f"Unknown database version: {args.db} not found in influx_keys. Aborting.")
    sys.exit(1)
elif not 'POST' in influx_keys[args.db]:
    print(f"POST URL not found in influx_keys[{args.db}]. Aborting.")
    sys.exit(1)
elif not 'GET-v1' in influx_keys[args.db]:
    print(f"GET-v1 URL not found in influx_keys[{args.db}]. Aborting.")
    print(f"GET-v1 is required to make InfluxQL-language queries to InfluxDB.")
    sys.exit(1)
elif not 'token' in influx_keys[args.db]:
    print(f"Influx token not found in influx_keys[{args.db}]. Aborting.")
    sys.exit(1)

# Checking succeeded - global setup of URIs and tokens
post_influx_uri = influx_keys[args.db]['POST']
# GET-v1 required to make InfluxQL-style queries
get_influx_uri = influx_keys[args.db]['GET-v1'] 
influx_token = influx_keys[args.db]['token']

# SELECT query - gets other tag information to re-post #########################
tags = StatusFile.INFLUX_TAGS
# These are some commonly needed fields, so we're going to gather these to re-post them in the new record
fields = StatusFile.INFLUX_FIELDS

tagline = ','.join([f"{fld}::tag" for fld in tags])
fieldline = ','.join([f"{fld}::field" for fld in fields if not (fld == 'event_name' or fld == 'event_value' or fld == 'user')])
fieldline += ',"user"'

event_selector = "last(event_name::field) AS event_name, event_value::field"
where_cond = f"test_id::tag = '{args.testid}'"
if args.event:
    event_selector = "event_name::field AS event_name, event_value::field"
    where_cond += f" AND event_name::field = '{args.event}'"

query = f"SELECT {tagline},{fieldline},{event_selector} FROM events WHERE {where_cond} GROUP BY test_id"
required_entries = ['test', 'app', 'test_id', 'runtag', 'machine', 'event_name', 'event_value']
################################################################################

def check_data(entry):
    # Check if all required columns exist ######################################
    missing_entries = []
    for req in required_entries:
        if not req in entry:
            missing_entries.append(req)
    if len(missing_entries) > 0:
        return [ False, f"Missing entries: {','.join(missing_entries)}" ]
    return [True, '']

def query_influx():
    """
        Send the query to get all running jobs
    """
    headers = {
        'Authorization': "Token " + influx_token,
        'Accept': "application/json"
    }
    print(query)
    url = f"{get_influx_uri}&db=accept&q={urllib.parse.quote(query)}"
    try:
        r = requests.get(url, headers=headers, params={'q': 'requests+language:python'})
    except requests.exceptions.ConnectionError as e:
        print("InfluxDB is not reachable. Request not sent.")
        print(str(e))
        sys.exit(1)
    except Exception as e:
        print(f"Failed to send to {url}:")
        print(str(e))
        sys.exit(2)
    print(r)
    resp = r.json()
    print(resp)
    if not 'series' in resp['results'][0]:
        print(f"No Running tests found.\nFull query: {query}.\nFull response: {resp}")
        return []
    # each entry in series is a record
    col_names = resp['results'][0]['series'][0]['columns']
    values = resp['results'][0]['series'][0]['values']
    if not len(values) == 1:
        print(f"Query returned {len(values)} results, expected 1. Exiting.")
        sys.exit(1)
    # Let's do the work of transforming this into a list of dicts
    ret_data = {}
    for c_index in range(0, len(col_names)):
        ret_data[col_names[c_index]] = values[0][c_index]
    should_add, reason = check_data(ret_data)
    if not should_add:
        test_id = data_tmp['test_id'] if 'test_id' in data_tmp else 'unknown'
        print(f"Invalid record associated with test_id {test_id}. Reason: {reason}. Exiting.")
        sys.exit(1)
    return ret_data

def post_update_to_influx(d):
    """ POSTs updated event to Influx """
    headers = {
        'Authorization': "Token " + influx_token,
        'Content-Type': "application/octet-stream",
        'Accept': "application/json"
    }
        #'Content-Type': "text/plain; charset=utf-8",
    try:
        log_time = datetime.datetime.strptime(d['time'], "%Y-%m-%dT%H:%M:%S.%fZ") - datetime.timedelta(hours=4)
    except ValueError as e:
        try:
            log_time = datetime.datetime.strptime(d['time'], "%Y-%m-%dT%H:%M:%SZ") - datetime.timedelta(hours=4)
            print(f"Time parsing with 'Y-m-dTH:M:S.msZ' failed. Attempting without microseconds.")
        except ValueError as e:
            raise ValueError(e)
    # Assume it's in UTC right now, convert to EST

    log_ns = round(datetime.datetime.timestamp(log_time) * 1000 * 1000) * 1000

    tagline = ','.join([f"{fld}={d[fld]}" for fld in tags])
    fieldline = ','.join([f"{fld}=\"{d[fld]}\"" for fld in fields])
    influx_event_record_string = f'events,{tagline} {fieldline} {str(log_ns)}'
    try:
        r = requests.post(post_influx_uri, data=influx_event_record_string, headers=headers)
        if int(r.status_code) < 400:
            print(f"Successfully updated {d['test_id']} with {influx_event_record_string}.")
            return True
        else:
            print(f"Influx returned status code: {r.status_code} in response to data: {influx_event_record_string}")
            print(r.text)
            return False
    except requests.exceptions.ConnectionError as e:
        print(f"InfluxDB is not reachable. Request not sent: {influx_event_record_string}")
        os.chdir(currentdir)
        return False
    except Exception as e:
        # TODO: add more graceful handling of unreachable influx servers
        print(f"Failed to send {influx_event_record_string} to {influx_url}:")
        print(e)
        os.chdir(currentdir)
        return False

data = query_influx()

timestamp = datetime.datetime.now().isoformat()

if data['comment'] and not data['comment'] == '[NO_VALUE]':
    print(f"Warning: found an existing comment on this record: {data['comment']}.\nAppending to this comment.")
    data['comment'] += f"\n{timestamp} - {os.environ['USER']}: {args.message}"
else:
    data['comment'] = f"{timestamp} - {os.environ['USER']}: {args.message}."

post_update_to_influx(data)

sys.exit(0)
