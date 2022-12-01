#!/usr/bin/env python3

################################################################################
# Author: Nick Hagerty
# Date modified: 11-28-2022
################################################################################
# Purpose:
#   Only intended for SLURM systems.
#   Queries InfluxDB to get the runs listed as currently running. Then,
#   queries SLURM to find out if the job crashed or not. POSTs the update
#   back to Influx under 'check_end' status.
################################################################################
# Edit note -- 11-28-2022 -- This script was Flux-ified. Influx v2 is now
#   required.
################################################################################

import os
import requests
import subprocess
import urllib.parse
from datetime import datetime
import argparse
import csv

try:
    from status_file import StatusFile
except:
    raise ImportError('Could not import status_file.py. Please make sure the olcf_harness module is loaded.')


# Initialize argparse ##########################################################
parser = argparse.ArgumentParser(description="Updates harness runs in InfluxDB with SLURM data")
parser.add_argument('--time', '-t', default='7d', type=str, action='store', help="How far back to look for jobs in Influx relative to now (ex: 1h, 2d).")
parser.add_argument('--starttime', type=str, action='store', help="Absolute start time. Format: YYYY-MM-DDTHH:MM:SSZ. Overrides --time")
parser.add_argument('--endtime', type=str, action='store', help="Absolute end time. Format: YYYY-MM-DDTHH:MM:SSZ. Should only be used with --starttime.")
parser.add_argument('--user', '-u', default=f"{os.environ['USER']}", type=str, action='store', help="Specifies the UNIX user to update jobs for.")
parser.add_argument('--machine', '-m', required=True, type=str, action='store', help="Specifies the machine to look for jobs for. Setting a wrong machine may lead to SLURM job IDs not being found.")
parser.add_argument('--app', type=str, action='store', help="Specifies the app to update jobs for.")
parser.add_argument('--test', type=str, action='store', help="Specifies the test to update jobs for.")
parser.add_argument('--runtag', type=str, action='store', help="Specifies the runtag to update jobs for.")
parser.add_argument('--db', type=str, default='dev', action='store', help="InfluxDB instance name to log to.")
parser.add_argument('--verbosity', '-v', default=0, type=int, action='store', help="InfluxDB instance name to log to.")
parser.add_argument('--dry-run', action='store_true', help="When set, prints messages to send to Influx, but does not send them.")
parser.add_argument('--force', '-f', action='store_true', help="When set, prints messages to send to Influx, but does not send them.")
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
if args.starttime:
    # Check format
    check_time_format(args.starttime)
if args.endtime:
    # Check format
    check_time_format(args.endtime)
if not (args.time.endswith('d') or args.time.endswith('h')):
    print(f"Unrecognized time parameter: {args.time[0]}.")
    print(f"This program allows hours or days to be specified as '1h' or '1d' for one hour or day, respectively.")
    exit(1)

flux_time_str = ''
# Build range() line for flux query
if args.starttime:
    # Then we use 'from: <timestamp>'
    flux_time_str = f'|> range(start: {args.starttime}'
    if args.endtime:
        flux_time_str += f', stop: {args.endtime}'
    flux_time_str += ')'
else:
    # Then we use --time
    flux_time_str = f'|> range(start: -{args.time})'

################################################################################

# SELECT query #################################################################
machine_app_test_filter = f'r.machine == "{args.machine}"'
if args.app:
    machine_app_test_filter += f' and r.app == "{args.app}"'
if args.test:
    machine_app_test_filter += f' and r["test"] == "{args.test}"'

def wrap_in_quotes(s):
    return f'"{s}"'

#sub_running_query = f"SELECT {', '.join([f'{t}::tag' for t in StatusFile.INFLUX_TAGS])}, job_id::field AS slurm_jobid, \"user\" AS username, last(event_name::field) AS current_status, event_value::field AS e_value FROM events {time_filter} GROUP BY test_id"
#running_query = f"SELECT {', '.join([t for t in StatusFile.INFLUX_TAGS])}, slurm_jobid, username, current_status, e_value FROM ({sub_running_query}) WHERE (current_status != 'check_end' AND (e_value = '0' OR e_value = '[NO_VALUE]')) OR current_status = 'job_queued'"
running_query = f'from(bucket: "accept") {flux_time_str} \
|> filter(fn: (r) => r._measurement == "events" and {machine_app_test_filter} and (r._field == "job_id" or r._field == "user" or r._field == "event_value" or r._field == "event_name")) \
|> last() \
|> pivot(rowKey: ["test_id", "machine", "_time"], columnKey: ["_field"], valueColumn: "_value") \
|> filter(fn: (r) => r.event_name == "job_queued" or (r.event_name != "check_end" and (r.event_value == "0" or r.event_value == "[NO_VALUE]"))) \
|> group() \
|> keep(columns: ["_time", {", ".join([wrap_in_quotes(t) for t in StatusFile.INFLUX_TAGS])}, "job_id", "user", "event_name", "event_value"])'

required_entries = [t for t in StatusFile.INFLUX_TAGS]
required_entries.extend(['job_id', 'user'])
################################################################################

# Global parameters extracted for ease of use ##################################
state_to_value = {
    'fail': 21,
    'timeout': 23,
    'node_fail': 9,
    'success': 0
}
job_state_codes = {
    'fail': ['DEADLINE', 'FAILED', 'OUT_OF_MEMORY', 'REVOKED'],
    'timeout': ['TIMEOUT'],
    'node_fail': ['NODE_FAIL', 'BOOT_FAIL', 'RESIZING'],
    'success': ['COMPLETED'],
    'pending': ['PENDING', 'RUNNING']
}
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
    # Check if the user matches ################################################
    if not entry['user'] == args.user:
        return [ False,
            f"Username of record ({entry['user']}) does not match requested user ({args.user})."]
    # Ensure job_id is non-null
    if entry['job_id'] == '[NO_VALUE]':
        return [ False,
            f"SLURM job ID is [NO_VALUE]."]
    # End checks
    return [True, '']

def query_influx_running():
    """
        Send the query to get all running jobs
    """
    headers = {
        'Authorization': "Token " + influx_token,
        'Content-type': 'application/vnd.flux',
        'Accept': "application/json"
    }
    url = f"{get_influx_uri}"
    print_debug(2, f"Running: {running_query} on {url}")
    try:
        r = requests.post(url, headers=headers, data=running_query)
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
            elif not (col_names[c_index] == "result" or col_names[c_index] == "table"):
                data_tmp[col_names[c_index]] = resp[entry_index][c_index]
        should_add, reason = check_data(data_tmp)
        if should_add:
            ret_data.append(data_tmp)
        else:
            jobid = data_tmp['test_id'] if 'test_id' in data_tmp else 'unknown'
            print_debug(2, f"Skipping test_id {jobid}. Reason: {reason}")
    return ret_data

def post_update_to_influx(d, state_code):
    """ POSTs updated event to Influx """
    d['event_name'] = 'check_end'
    d['event_value'] = state_to_value[state_code]

    headers = {
        'Authorization': "Token " + influx_token,
        'Content-Type': "application/octet-stream",
        'Accept': "application/json"
    }
        #'Content-Type': "text/plain; charset=utf-8",
    if not 'timestamp' in d.keys():
        d['timestamp'] = datetime.datetime.now().isoformat()
    log_time = datetime.strptime(d['timestamp'], "%Y-%m-%dT%H:%M:%S")
    log_ns = int(datetime.timestamp(log_time) * 1000 * 1000) * 1000

    influx_event_record_string = f"events,{','.join([f'{t}={d[t]}' for t in StatusFile.INFLUX_TAGS])} "
    quote = '"'
    influx_event_record_string += f"{','.join([f'{t}={quote}{d[t]}{quote}' for t in d if (not t == 'timestamp') and (not t in StatusFile.INFLUX_TAGS)])}"
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

def check_job_status(slurm_jobid_lst):
    """
        Checks if a Slurm job is running by querying sacct
        Returns [False] (list length=1) or
            [JobID, Elapsed, Start, End, State, ExitCode, Reason, Comment]
    """
    result = {}  # a dictionary of dictionaries
    low_limit = 0
    high_limit = 0
    batch_size = 100
    node_failed_jobids = []
    print_debug(2, f"Querying sacct with {len(slurm_jobid_lst)} jobs in batches of up to {batch_size}")
    # Batched into batches of 100
    while low_limit < len(slurm_jobid_lst):
        high_limit = min(low_limit + batch_size, len(slurm_jobid_lst))
        sacct_format = 'JobID,Elapsed,Start,End,State%40,ExitCode,Reason%100,Comment%100'
        cmd=f"sacct -j {','.join(slurm_jobid_lst[low_limit:high_limit])} --format {sacct_format} -X"
        os.system(f'{cmd} 2>&1 > slurm.jobs.tmp.txt')
        with open(f'slurm.jobs.tmp.txt', 'r') as f:
            line = f.readline()
            labels = line.split()
            comment_line = f.readline()   # line of dashes
            # use the spaces in the comment line to split the next line properly
            for line in f:
                fields = {}
                search_pos = -1
                for i in range(0, len(labels)):
                    next_space = comment_line.find(' ', search_pos + 1)
                    # No more spaces found, and it's the last label
                    if next_space < 0 and i == len(labels) - 1:
                        next_space = len(line)
                    elif next_space < 0:
                        print_debug(1, f"Couldn't find enough spaces to correctly parse the columns to fit the labels {','.join(labels)}")
                    cur_field = line[search_pos+1:next_space].strip()
                    search_pos = next_space
                    fields[labels[i].lower()] = cur_field
                if not 'jobid' in fields:
                    print_debug(0, f"Couldn't find JobID in sacct record. Skipping")
                    continue
                elif fields['state'] == 'RESIZING':
                    print_debug(1, f"Detected RESIZING for job {fields['jobid']}. RESIZING is from node failure + SLURM '--no-kill'. There should be another record in sacct for this job. Skipping")
                    # Add a field to this job that shows it had/survived a node failure
                    node_failed_jobids.append(fields['jobid'])
                    continue
                elif fields['jobid'] in node_failed_jobids:
                    # Check if a previous step had come in with RESIZING
                    print_debug(1, f"Found jobid in node failure list: {fields['jobid']}")
                    fields['node-failed'] = True
                result[fields['jobid']] = fields
        os.remove(f"slurm.jobs.tmp.txt")
        low_limit = high_limit  # prepare for next iteration
    return result

def get_user_from_id(user_id):
    """ Given a user ID, return the username """
    # replace parenthesis with commas to make splitting easier
    os.system(f"id {user_id} 2>&1 | tr '()' '??' | cut -d'?' -f2 > tmp.user.txt")
    with open(f'tmp.user.txt', 'r') as f:
        user_name = f.readline().strip()
    if len(user_name) == 0:
        print_debug(1, f"Couldn't find user name for {user_id}. Returning 'unknown'")
        user_name = 'unknown'
    os.remove(f"tmp.user.txt")
    return user_name


data = query_influx_running()
# This is safe, since each entry has already been checked for slurm_jobid
slurm_job_ids = [ e['job_id'] for e in data ]

# A job ID will have a field named `node-failed` = True if it survived a node failure via --no-kill
slurm_data = check_job_status(slurm_job_ids)

skipped = 0

for entry in data:
    # check to see if this entry should be parsed
    print_debug(1, f"Processing {entry['test_id']}, SLURM id {entry['job_id']} ========================")
    d = {
        'job_id': entry['job_id']
    }
    for t in StatusFile.INFLUX_TAGS:
        d[t] = entry[t]
    if not entry['job_id'] in slurm_data:
        print_debug(1, f"Can't find data for {entry['job_id']} in sacct data. Skipping")
        skipped += 1
        continue
    if slurm_data[entry['job_id']]['state'] in job_state_codes['fail']:
        print_debug(1, f"Found failed job {entry['job_id']}. Sending status to Influx.")
        d['timestamp'] = slurm_data[entry['job_id']]['end']
        d['reason'] = f"Job exited in state {slurm_data[entry['job_id']]['state']} at {slurm_data[entry['job_id']]['end']}, after running for {slurm_data[entry['job_id']]['elapsed']}."
        d['reason'] += f" Exit code: {slurm_data[entry['job_id']]['exitcode']}, reason: {slurm_data[entry['job_id']]['reason']}."
        d['comment'] = slurm_data[entry['job_id']]['comment']
        post_update_to_influx(d, 'fail')
    elif slurm_data[entry['job_id']]['state'].startswith('CANCELLED'):
        print_debug(1, f"Found cancelled job {d['job_id']}. Sending status to Influx.")
        if 'node-failed' in slurm_data[entry['job_id']] and slurm_data[entry['job_id']]['node-failed']:
            d['reason'] = 'NODE_FAIL detected. Job canceled'
        else:
            d['reason'] = 'Job canceled'
        d['timestamp'] = slurm_data[entry['job_id']]['end']
        d['comment'] = slurm_data[entry['job_id']]['comment']
        # Check if CANCELLED BY ...
        job_status_long = slurm_data[entry['job_id']]['state'].split(' ')
        if len(job_status_long) > 1:
            cancel_user = get_user_from_id(job_status_long[2])
            d['reason'] = f" at {slurm_data[entry['job_id']]['end']} by {cancel_user}"
        else:
            d['reason'] = f" at {slurm_data[entry['job_id']]['end']}"
        d['reason'] += f", after running for {slurm_data[entry['job_id']]['elapsed']}."
        d['reason'] += f" Exit code: {slurm_data[entry['job_id']]['exitcode']}, reason: {slurm_data[entry['job_id']]['reason']}."
        post_update_to_influx(d, 'fail')
    elif slurm_data[entry['job_id']]['state'] in job_state_codes['node_fail']:
        print_debug(1, f"Found node_failure in: {d['job_id']}")
        d['timestamp'] = slurm_data[entry['job_id']]['end']
        d['reason'] = f"Node failure detected. Job exited in state {slurm_data[entry['job_id']]['state']} at {slurm_data[entry['job_id']]['end']}, after running for {slurm_data[entry['job_id']]['elapsed']}."
        post_update_to_influx(d, 'node_fail')
    elif slurm_data[entry['job_id']]['state'] in job_state_codes['timeout']:
        if 'node-failed' in slurm_data[entry['job_id']] and slurm_data[entry['job_id']]['node-failed']:
            print_debug(1, f"Found timed out job: {d['job_id']}")
            d['reason'] = f"NODE_FAIL followed by TIMEOUT detected. Job exited in state {slurm_data[entry['job_id']]['state']} at {slurm_data[entry['job_id']]['end']}, after running for {slurm_data[entry['job_id']]['elapsed']}."
            d['timestamp'] = slurm_data[entry['job_id']]['end']
            post_update_to_influx(d, 'node_fail')
        else:
            print_debug(1, f"Found timed out job: {d['job_id']}")
            d['reason'] = f"TIMEOUT detected. Job exited in state {slurm_data[entry['job_id']]['state']} at {slurm_data[entry['job_id']]['end']}, after running for {slurm_data[entry['job_id']]['elapsed']}."
            d['timestamp'] = slurm_data[entry['job_id']]['end']
            post_update_to_influx(d, 'timeout')
    elif slurm_data[entry['job_id']]['state'] in job_state_codes['success']:
        if args.force:
            print_debug(1, f"Marking job as completed: {d['job_id']}")
            d['timestamp'] = slurm_data[entry['job_id']]['end']
            post_update_to_influx(d, 'success')
        else:
            csv_str = '{' + f"app={d['app']},test={d['test']},test_id={d['test_id']},job_id={d['job_id']}" + '}'
            print_debug(0, f"Found a job marked as completed: {csv_str}. Harness mode influx_log preferred. Please use --force to override this.")
    elif slurm_data[entry['job_id']]['state'] in job_state_codes['pending']:
        print_debug(1, f"Job {d['job_id']} is still pending. No action is being taken.")
        skipped += 1
    else:
        print_debug(0, f"Unrecognized job state: {slurm_data[entry['job_id']]['state']}. No action is being taken.")
        skipped += 1


print_debug(0, f"{len(data) - skipped} entries sent to InfluxDB. {skipped} skipped.")
exit(0)
