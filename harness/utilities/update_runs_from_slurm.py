#!/usr/bin/env python3

################################################################################
# Author: Nick Hagerty
# Date modified: 11-14-2022
################################################################################
# Purpose:
#   Only intended for SLURM systems.
#   Queries InfluxDB to get the runs listed as currently running. Then,
#   queries SLURM to find out if the job crashed or not. POSTs the update
#   back to Influx under 'check_end' status.
################################################################################
################################################################################

import os
import requests
import subprocess
import urllib.parse
from datetime import datetime
import argparse

try:
    from status_file import StatusFile
except:
    raise ImportError('Could not import status_file.py. Please make sure the olcf_harness module is loaded.')


# Initialize argparse ##########################################################
parser = argparse.ArgumentParser(description="Updates harness runs in InfluxDB with SLURM data")
parser.add_argument('--time', '-t', default=['14d'], nargs=1, action='store', help="How far back to look for jobs in Influx (ex: 1h, 2d). 'none' disables this filter.")
parser.add_argument('--user', '-u', default=[f"{os.environ['USER']}"], nargs=1, action='store', help="Specifies the UNIX user to update jobs for.")
parser.add_argument('--machine', '-m', required=True, nargs=1, action='store', help="Specifies the machine to look for jobs for. Setting a wrong machine may lead to SLURM job IDs not being found.")
parser.add_argument('--app', nargs=1, action='store', help="Specifies the app to update jobs for.")
parser.add_argument('--test', nargs=1, action='store', help="Specifies the test to update jobs for.")
parser.add_argument('--runtag', nargs=1, action='store', help="Specifies the runtag to update jobs for.")
parser.add_argument('--db', nargs=1, default=['dev'], action='store', help="InfluxDB instance name to log to.")
parser.add_argument('--verbosity', '-v', default=0, type=int, action='store', help="InfluxDB instance name to log to.")
parser.add_argument('--dry-run', action='store_true', help="When set, prints messages to send to Influx, but does not send them.")
################################################################################

# Global URIs and Tokens #######################################################
from harness_keys import influx_keys
################################################################################

# Parse command-line arguments #################################################
args = parser.parse_args()

# Set up URIs and Tokens #######################################################
if not args.db[0] in influx_keys.keys():
    print(f"Unknown database version: {args.db[0]} not found in influx_keys. Aborting.")
    exit(1)
elif not 'POST' in influx_keys[args.db[0]]:
    print(f"POST URL not found in influx_keys[{args.db[0]}]. Aborting.")
    exit(1)
elif not 'GET' in influx_keys[args.db[0]]:
    print(f"GET URL not found in influx_keys[{args.db[0]}]. Aborting.")
    exit(1)
elif not 'token' in influx_keys[args.db[0]]:
    print(f"Influx token not found in influx_keys[{args.db[0]}]. Aborting.")
    exit(1)

# Checking succeeded - global setup of URIs and tokens
post_influx_uri = influx_keys[args.db[0]]['POST']
get_influx_uri = influx_keys[args.db[0]]['GET']
influx_token = influx_keys[args.db[0]]['token']

# Check command-line arguments #################################################
if args.time[0] == 'none':
    time_filter = ''
elif args.time[0].endswith('d') or args.time[0].endswith('h'):
    time_filter = f"WHERE time >= now() - {args.time[0]} AND time <= now()"
else:
    print(f"Unrecognized time parameter: {args.time[0]}.")
    print(f"This program allows hours or days to be specified as '1h' or '1d' for one hour or day, respectively.")
    exit(1)

################################################################################

# SELECT query #################################################################
sub_running_query = f"SELECT {', '.join([f'{t}::tag' for t in StatusFile.INFLUX_TAGS])}, job_id::field AS slurm_jobid, \"user\" AS username, last(event_name::field) AS current_status, event_value::field AS e_value FROM events {time_filter} GROUP BY test_id"
running_query = f"SELECT {', '.join([t for t in StatusFile.INFLUX_TAGS])}, slurm_jobid, username, current_status, e_value FROM ({sub_running_query}) WHERE (current_status != 'check_end' AND (e_value = '0' OR e_value = '[NO_VALUE]')) OR current_status = 'job_queued'"
required_entries = [t for t in StatusFile.INFLUX_TAGS]
required_entries.extend(['slurm_jobid', 'username'])
################################################################################

# Global parameters extracted for ease of use ##################################
state_to_value = {
    'fail': 21,
    'timeout': 21,
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
    if not entry['username'] == args.user[0]:
        return [ False,
            f"Username of record ({entry['username']}) does not match requested user ({args.user[0]})."]
    # Check if the app matches ################################################
    if args.app and not entry['app'] == args.app[0]:
        return [ False,
            f"App of record ({entry['app']}) does not match requested app ({args.app[0]})."]
    # Check if the runtag matches ##############################################
    if args.runtag and not entry['runtag'] == args.runtag[0]:
        return [ False,
            f"Runtag of record ({entry['runtag']}) does not match requested runtag ({args.runtag[0]})."]
    # Check if the test matches ##################################################
    if args.test and not entry['test'] == args.test[0]:
        return [ False,
            f"Test of record ({entry['test']}) does not match requested test ({args.test[0]})."]
    if entry['slurm_jobid'] == '[NO_VALUE]':
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
        'Accept': "application/json"
    }
    url = f"{get_influx_uri}&db=accept&q={urllib.parse.quote(running_query)}"
    try:
        r = requests.get(url, headers=headers, params={'q': 'requests+language:python'})
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
    resp = r.json()
    if not 'series' in resp['results'][0]:
        print_debug(1, f"No Running tests found. Full response: {resp}")
        return []
    # each entry in series is a record
    col_names = resp['results'][0]['series'][0]['columns']
    values = resp['results'][0]['series'][0]['values']
    # Let's do the work of transforming this into a list of dicts
    ret_data = []
    for entry_index in range(0, len(values)):
        data_tmp = {}
        for c_index in range(0, len(col_names)):
            data_tmp[col_names[c_index]] = values[entry_index][c_index]
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
        cmd=f"sacct -j {','.join(slurm_jobid_lst[low_limit:high_limit])} --format {sacct_format}"
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
slurm_job_ids = [ e['slurm_jobid'] for e in data ]

# A job ID will have a field named `node-failed` = True if it survived a node failure via --no-kill
slurm_data = check_job_status(slurm_job_ids)

skipped = 0

for entry in data:
    # check to see if this entry should be parsed
    print_debug(1, f"Processing {entry['test_id']}, SLURM id {entry['slurm_jobid']} ========================")
    d = {
        'job_id': entry['slurm_jobid']
    }
    for t in StatusFile.INFLUX_TAGS:
        d[t] = entry[t]
    if not entry['slurm_jobid'] in slurm_data:
        print_debug(1, f"Can't find data for {entry['slurm_jobid']} in sacct data. Skipping")
        skipped += 1
        continue
    if slurm_data[entry['slurm_jobid']]['state'] in job_state_codes['fail']:
        print_debug(1, f"Found failed job {entry['slurm_jobid']}. Sending status to Influx.")
        d['timestamp'] = slurm_data[entry['slurm_jobid']]['end']
        d['reason'] = f"Job exited in state {slurm_data[entry['slurm_jobid']]['state']} at {slurm_data[entry['slurm_jobid']]['end']}, after running for {slurm_data[entry['slurm_jobid']]['elapsed']}."
        d['reason'] += f" Exit code: {slurm_data[entry['slurm_jobid']]['exitcode']}, reason: {slurm_data[entry['slurm_jobid']]['reason']}."
        d['comment'] = slurm_data[entry['slurm_jobid']]['comment']
        post_update_to_influx(d, 'fail')
    elif slurm_data[entry['slurm_jobid']]['state'].startswith('CANCELLED'):
        print_debug(1, f"Found cancelled job {d['job_id']}. Sending status to Influx.")
        d['timestamp'] = slurm_data[entry['slurm_jobid']]['end']
        d['comment'] = slurm_data[entry['slurm_jobid']]['comment']
        # Check if CANCELLED BY ...
        job_status_long = slurm_data[entry['slurm_jobid']]['state'].split(' ')
        if len(job_status_long) > 1:
            cancel_user = get_user_from_id(job_status_long[2])
            d['reason'] = f" Job canceled at {slurm_data[entry['slurm_jobid']]['end']} by {cancel_user}"
        else:
            d['reason'] = f"Job cancelled at {slurm_data[entry['slurm_jobid']]['end']}"
        d['reason'] += f", after running for {slurm_data[entry['slurm_jobid']]['elapsed']}."
        d['reason'] += f" Exit code: {slurm_data[entry['slurm_jobid']]['exitcode']}, reason: {slurm_data[entry['slurm_jobid']]['reason']}."
        post_update_to_influx(d, 'fail')
    elif slurm_data[entry['slurm_jobid']]['state'] in job_state_codes['node_fail']:
        print_debug(1, f"Found node_failure in: {d['job_id']}")
        d['timestamp'] = slurm_data[entry['slurm_jobid']]['end']
        d['reason'] = f"Node failure detected. Job exited in state {slurm_data[entry['slurm_jobid']]['state']} at {slurm_data[entry['slurm_jobid']]['end']}, after running for {slurm_data[entry['slurm_jobid']]['elapsed']}."
        post_update_to_influx(d, 'node_fail')
    elif slurm_data[entry['slurm_jobid']]['state'] in job_state_codes['timeout']:
        print_debug(1, f"Found timed out job: {d['job_id']}")
        d['timestamp'] = slurm_data[entry['slurm_jobid']]['end']
        d['reason'] = f"TIMEOUT detected. Job exited in state {slurm_data[entry['slurm_jobid']]['state']} at {slurm_data[entry['slurm_jobid']]['end']}, after running for {slurm_data[entry['slurm_jobid']]['elapsed']}."
        post_update_to_influx(d, 'timeout')
    elif slurm_data[entry['slurm_jobid']]['state'] in job_state_codes['success']:
        print_debug(1, f"Marking job as completed: {d['job_id']}")
        d['timestamp'] = slurm_data[entry['slurm_jobid']]['end']
        post_update_to_influx(d, 'success')
    elif slurm_data[entry['slurm_jobid']]['state'] in job_state_codes['pending']:
        printi_debug(1, f"Job {d['job_id']} is still pending. No action is being taken.")
        skipped += 1
    else:
        print_debug(0, f"Unrecognized job state: {slurm_data[entry['slurm_jobid']]['state']}. No action is being taken.")
        skipped += 1


print_debug(0, f"{len(data) - skipped} entries sent to InfluxDB. {skipped} skipped.")
exit(0)
