#!/usr/bin/env python3

################################################################################
# Author: Nick Hagerty
# Date modified: 08-25-2022
################################################################################
# Purpose:
#   Allows users to change the machine a harness job is logged to in InfluxDB.
################################################################################
# Warning:
#   This script will effectively duplicate a record in InfluxDB. The old record
#   cannot be permanently removed. Accidentally duplicating records for another
#   machine will make a big mess.
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
parser = argparse.ArgumentParser(description="Updates harness run in InfluxDB with a new machine name")
parser.add_argument('--testid', '-t', nargs=1, action='store', required=True, help="Specifies the harness test ID to update machine for.")
parser.add_argument('--newmachine', '-m', nargs=1, action='store', required=True, help="New machine to assign to the harness test.")
parser.add_argument('--db', nargs=1, default=['dev'], action='store', help="InfluxDB instance name to log to.")
################################################################################

# Global URIs and Tokens #######################################################
from harness_keys import influx_keys
################################################################################

# Parse command-line arguments #################################################
args = parser.parse_args()  # event field already validated by 'choices'

# Set up URIs and Tokens #######################################################
if not args.db[0] in influx_keys.keys():
    print(f"Unknown database version: {args.db[0]} not found in influx_keys. Aborting.")
    sys.exit(1)
elif not 'POST' in influx_keys[args.db[0]]:
    print(f"POST URL not found in influx_keys[{args.db[0]}]. Aborting.")
    sys.exit(1)
elif not 'GET' in influx_keys[args.db[0]]:
    print(f"GET URL not found in influx_keys[{args.db[0]}]. Aborting.")
    sys.exit(1)
elif not 'token' in influx_keys[args.db[0]]:
    print(f"Influx token not found in influx_keys[{args.db[0]}]. Aborting.")
    sys.exit(1)

# Checking succeeded - global setup of URIs and tokens
post_influx_uri = influx_keys[args.db[0]]['POST']
get_influx_uri = influx_keys[args.db[0]]['GET']
influx_token = influx_keys[args.db[0]]['token']

# SELECT query - gets other tag information to re-post #########################
tags = StatusFile.INFLUX_TAGS
# These are some commonly needed fields, so we're going to gather these to re-post them in the new record
fields = StatusFile.INFLUX_FIELDS

tagline = ','.join([f"{fld}::tag" for fld in tags])
fieldline = ','.join([f"{fld}::field" for fld in fields if not fld == 'user'])
fieldline += ',"user"'

where_cond = f"test_id::tag = '{args.testid[0]}'"

query = f"SELECT {tagline},{fieldline} FROM events WHERE {where_cond}"
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
    resp = r.json()
    if not 'series' in resp['results'][0]:
        print(f"No Running tests found.\nFull query: {query}.\nFull response: {resp}")
        return []
    # each entry in series is a record
    col_names = resp['results'][0]['series'][0]['columns']
    values = resp['results'][0]['series'][0]['values']
    ret_data = []
    for v in range(0, len(values)):
        # Let's do the work of transforming this into a list of dicts
        tmp_d = {}
        for c_index in range(0, len(col_names)):
            tmp_d[col_names[c_index]] = values[v][c_index]
        should_add, reason = check_data(tmp_d)
        if not should_add:
            test_id = tmp_d['test_id'] if 'test_id' in tmp_d else 'unknown'
            print(f"Invalid record associated with test_id {test_id}. Reason: {reason}. Exiting.")
            sys.exit(1)
        ret_data.append(tmp_d)
    return ret_data

def post_update_to_influx(d):
    """ POSTs updated event to Influx """
    headers = {
        'Authorization': "Token " + influx_token,
        'Content-Type': "application/octet-stream",
        'Accept': "application/json"
    }
        #'Content-Type': "text/plain; charset=utf-8",
    # This is provided in UTC -- convert to EST
    log_time = datetime.datetime.strptime(d['time'], "%Y-%m-%dT%H:%M:%S.%fZ") - datetime.timedelta(hours=4)
    # microsecond timing max precision
    log_ns = int(datetime.datetime.timestamp(log_time) * 1000 * 1000) * 1000

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

# set d['timestamp'] to set a timestamp
timestamp = datetime.datetime.now().isoformat()
# reason or comment field

for d in data:
    old_machine = d['machine']
    if d['comment'] and not d['comment'] == '[NO_VALUE]':
        d['comment'] += f"\n{timestamp} - {os.environ['USER']}: machine name changed from {d['machine']} to {args.newmachine[0]}."
        d['machine'] = args.newmachine[0]
    else:
        d['comment'] = f"{timestamp} - {os.environ['USER']}: machine name changed from {d['machine']} to {args.newmachine[0]}."
        d['machine'] = args.newmachine[0]
    post_update_to_influx(d)

sys.exit(0)
