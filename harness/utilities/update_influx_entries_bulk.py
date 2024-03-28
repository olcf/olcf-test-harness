#!/usr/bin/env python3

################################################################################
# Author: Nick Hagerty
# Date modified: 03-19-2024
################################################################################
# Purpose:
#   Given a set of parameters to identify tests by, performs an edit action on
#   all records found matching the parameters. Useful for fixing user-error
#   issues that have been posted as failures.
################################################################################
# Requirements:
#   - This script requires the InfluxDB/v2 interface for Flux
################################################################################

import os
import requests
import subprocess
import urllib.parse
from datetime import datetime, timedelta
import argparse
import csv

try:
    from status_file import StatusFile
except:
    raise ImportError('Could not import status_file.py. Please make sure the olcf_harness module is loaded.')


# Initialize argparse ##########################################################
parser = argparse.ArgumentParser(description="Updates harness runs in InfluxDB with SLURM data")
parser.add_argument('--starttime', required=True, type=str, action='store', help="Absolute start time. Format: YYYY-MM-DDTHH:MM:SSZ. Overrides --time")
parser.add_argument('--endtime', type=str, action='store', help="Absolute end time. Format: YYYY-MM-DDTHH:MM:SSZ. Should only be used with --starttime.")
parser.add_argument('--user', '-u', type=str, action='store', help="Specifies the UNIX user to update jobs for.")
parser.add_argument('--machine', '-m', required=True, type=str, action='store', help="Specifies the machine to look for jobs for. This script does not need to be run from this machine.")
parser.add_argument('--test_id', type=str, action='store', help="Specifies the test_id to update jobs for.")
parser.add_argument('--app', type=str, action='store', help="Specifies the app to update jobs for.")
parser.add_argument('--test', type=str, action='store', help="Specifies the test to update jobs for.")
parser.add_argument('--runtag', type=str, action='store', help="Specifies the runtag to update jobs for.")
parser.add_argument('--db', type=str, default='dev', action='store', help="InfluxDB instance name to log to. Default: dev")
parser.add_argument('--verbosity', '-v', default=0, type=int, action='store', help="Verbosity level for stdout printing.")
parser.add_argument('--dry-run', action='store_true', help="When set, prints messages to send to Influx, but does not send them.")
parser.add_argument('--message', type=str, action='store', help="Specify a message to post in the 'comment' field of the new InfluxDB record.")
parser.add_argument('--new-check-status', type=int, default=4, action='store', help="Integer exit code to post with the check_end status. Default: 4.")
parser.add_argument('-y', action='store_true', help="USE WITH CAUTION: when set, bypasses the 'Are you sure?' message.")
################################################################################

# Global URIs and Tokens #######################################################
try:
    from harness_keys import influx_keys
except:
    raise ImportError('Could not import harness_keys.py. Please make sure that you have a file named harness_keys.py in the harness/utilities sub-directory. This is how this script reads information to query InfluxDB.')
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
get_influx_uri = influx_keys[args.db]['GET']
influx_token = influx_keys[args.db]['token']

# Build the time filter ########################################################
def check_time_format(s):
    try:
        dt = datetime.strptime(s, "%Y-%m-%dT%H:%M:%SZ")
    except Exception as e:
        print(f"Invalid time format: {s}. Aborting")
        print(str(e))
        raise
    return True

# Check time formatting
check_time_format(args.starttime)
if args.endtime:
    # Check format
    check_time_format(args.endtime)

flux_time_str = ''
# Build range() line for flux query
flux_time_str = f'|> range(start: {args.starttime}'
if args.endtime:
    flux_time_str += f', stop: {args.endtime}'
flux_time_str += ')'

################################################################################

# SELECT query #################################################################
filters = []
field_filters = []
if args.test_id:
    filters.append(f'r.test_id == "{args.test_id}"')
if args.machine:
    filters.append(f'r.machine == "{args.machine}"')
if args.app:
    filters.append(f'r.app == "{args.app}"')
if args.test:
    filters.append(f'r["test"] == "{args.test}"')
if args.runtag:
    filters.append(f'r.runtag == "{args.runtag}"')
if args.user:
    field_filters.append(f'r["user"] == "{args.user}"')

if len(filters) == 0:
    print("At least one of app, test, runtag, machine, or test_id is required")
    exit(1)

field_filter = ''
if len(field_filters) > 0:
    field_filter = f' and {" and ".join(field_filters)}'
# Excludes the output_txt field, since that's not important here
event_query = f'from(bucket: "accept") {flux_time_str} \
|> filter(fn: (r) => r._measurement == "events" and {" and ".join(filters)} and r._field != "output_txt") \
|> last() \
|> pivot(rowKey: ["test_id", "machine", "_time"], columnKey: ["_field"], valueColumn: "_value") \
|> filter(fn: (r) => r.event_name == "check_end"{field_filter}) \
|> group()'

required_entries = [t for t in StatusFile.INFLUX_TAGS]
required_entries.extend(['job_id', 'user'])
################################################################################

def print_debug(lvl, msg):
    if int(lvl) <= int(args.verbosity):
        print(f"{lvl}: {msg}")

def check_data(entry):
    # Check if all required columns exist ######################################
    missing_entries = []
    for req in required_entries:
        if not req in entry:
            missing_entries.append(req)
    if len(missing_entries) > 0:
        return [ False, f"Missing entries: {','.join(missing_entries)}" ]
    # End checks
    return [True, '']

def query_influx():
    """
        Send the query to get all jobs matching criteria
    """
    headers = {
        'Authorization': "Token " + influx_token,
        'Content-type': 'application/vnd.flux',
        'Accept': "application/json"
    }
    url = f"{get_influx_uri}"
    print_debug(2, f"Running: {event_query} on {url}")
    try:
        r = requests.post(url, headers=headers, data=event_query)
        if int(r.status_code) >= 400:
            print_debug(0, f"Influx request failed, status_code = {r.status_code}, text = {r.text}, reason = {r.reason}.")
            exit(1)
    except requests.exceptions.ConnectionError as e:
        print_debug(0, "InfluxDB is not reachable. Request not sent.")
        print_debug(0, str(e))
        exit(1)
    except Exception as e:
        print_debug(0, f"Failed to send to {url}:")
        print_debug(0, str(e))
        exit(2)
    rdc = r.content.decode('utf-8')
    resp = list(csv.reader(rdc.splitlines(), delimiter=','))
    # each entry in series is a record
    col_names = resp[0]
    # Let's do the work of transforming this into a list of dicts
    ret_data = []
    for entry_index in range(1, len(resp)):
        data_tmp = {}
        if len(resp[entry_index]) < len(col_names):
            print_debug(2, f"Length too short. Skipping row: {resp[entry_index]}.")
            continue
        # First column is useless
        for c_index in range(1, len(col_names)):
            # Ignore result, table & rename time
            if col_names[c_index] == "_time":
                data_tmp["time"] = resp[entry_index][c_index]
            elif not (col_names[c_index] == "result" or col_names[c_index] == "table" or col_names[c_index].startswith('_')):
                data_tmp[col_names[c_index]] = resp[entry_index][c_index]
        should_add, reason = check_data(data_tmp)
        if should_add:
            ret_data.append(data_tmp)
        else:
            jobid = data_tmp['test_id'] if 'test_id' in data_tmp else 'unknown'
            print_debug(2, f"Skipping test_id {jobid}. Reason: {reason}")
    return ret_data

def post_update_to_influx(d):
    """ POSTs updated event to Influx """
    # Construct message
    new_msg = ''
    standard_msg = f'Updated using the update_influx_entries_bulk.py utility script. Old check status: {d["event_value"]}, new check status: {args.new_check_status}'
    timestamp = datetime.now().isoformat()
    if args.message:
        new_msg = f'[{timestamp}] {os.environ["USER"]}: {args.message}. {standard_msg}.'
    else:
        new_msg = f'[{timestamp}] {os.environ["USER"]}: {standard_msg}.'
    # Set comment = message
    if d['comment'] and not d['comment'] == '[NO_VALUE]':
        d['comment'] = f'{d["comment"]}\n{new_msg}'
    else:
        d['comment'] = f'{new_msg}'
    # Set new check status
    d['event_value'] = args.new_check_status

    # Convert any double quotes into escaped double-quotes
    for field in d.keys():
        d[field] = d[field].replace('"', '\\"')

    headers = {
        'Authorization': "Token " + influx_token,
        'Content-Type': "application/octet-stream",
        'Accept': "application/json"
    }
    try:
        log_time = datetime.strptime(d['time'], "%Y-%m-%dT%H:%M:%S.%fZ") - timedelta(hours=5)
    except ValueError as e:
        try:
            log_time = datetime.strptime(d['time'], "%Y-%m-%dT%H:%M:%SZ") - timedelta(hours=5)
            print(f"Time parsing with 'Y-m-dTH:M:S.msZ' failed. Attempting without microseconds.")
        except ValueError as e:
            raise ValueError(e)
    log_ns = round(datetime.timestamp(log_time) * 1000 * 1000) * 1000

    influx_event_record_string = f"events,{','.join([f'{t}={d[t]}' for t in StatusFile.INFLUX_TAGS])} "
    quote = '"'
    influx_event_record_string += f"{','.join([f'{t}={quote}{d[t]}{quote}' for t in d if (not t == 'time') and (not t in StatusFile.INFLUX_TAGS)])}"
    influx_event_record_string += f' {str(log_ns)}'
    try:
        if not args.dry_run:
            r = requests.post(post_influx_uri, data=influx_event_record_string, headers=headers)
            if int(r.status_code) < 400:
                print_debug(1, f"Successfully updated {d['test_id']} with {influx_event_record_string}.")
                return True
            else:
                print_debug(0, f"Influx returned status code: {r.status_code} in response to data: {influx_event_record_string}")
                print_debug(1, r.text)
                return False
        else:
            print_debug(0, f"Dry run set. Message: {influx_event_record_string}")
    except requests.exceptions.ConnectionError as e:
        print_debug(0, f"InfluxDB is not reachable. Request not sent: {influx_event_record_string}")
        return False
    except Exception as e:
        # TODO: add more graceful handling of unreachable influx servers
        print_debug(0, f"Failed to send {influx_event_record_string} to {influx_url}:")
        print_debug(1, e)
        return False

data = query_influx()

print(f"Found {len(data)} total jobs to update")
num_updated = 0

for entry in data:
    do_update = 'y'
    if not args.y:
        do_update = input(f"Found test_id={entry['test_id']},job_id={entry['job_id']}. Update this entry? [y/n]: ")
    if do_update == 'y':
        post_update_to_influx(entry)
        num_updated += 1
    else:
        print_debug(1, f"Skipping {entry['test_id']}")

print_debug(0, f"{num_updated} entries sent to InfluxDB.")
exit(0)
