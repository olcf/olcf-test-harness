#!/usr/bin/env python3

################################################################################
# Author: Nick Hagerty
# Date modified: 07-25-2022
################################################################################
# Purpose:
#   Only intended for SLURM systems.
#   Queries InfluxDB to get the runs listed as currently running. Then,
#   queries SLURM to find out if the job crashed or not. POSTs the update
#   back to Influx under 'check_end' status. Failed jobs report 2, successful
#   report 0.
################################################################################
################################################################################

import os
import sys
import requests
import subprocess
import urllib.parse
from datetime import datetime

# Global URIs and Tokens #######################################################
from harness_keys import post_influx_uri, get_influx_uri, influx_token
################################################################################

# Parse command-line arguments #################################################
if len(sys.argv) == 2 and 'help' in sys.argv[1]:
    print(f"Usage: ./update_runs_from_slurm.py [args]")
    print(f"\t--time=<timestring>    : How far back to look for jobs in Influx. 'none' disables this filter.")
    print(f"\t--user=<username>      : Specifies the user to update jobs for.")
    print(f"\t--machine=<machine>    : Specifies the machine to look for jobs for.")
    print(f"\t                         WARNING: setting a wrong machine may lead to SLURM job IDs not being found.")
    print(f"\t--app=<app>            : Specifies the app to update jobs for.")
    print(f"\t--test=<test>          : Specifies the test to update jobs for.")
    print(f"\t--runtag=<runtag>      : Specifies the runtag to update jobs for.")
    sys.exit(0)

current_machine = 'unknown'
time_filter_length = '7d'   # default 7 days
# default filter to the current user
command_line_filters = {
    'user': os.environ['USER']
}
allowed_args = ['user', 'app', 'test', 'runtag']

usage = './update_runs_from_slurm.py --machine=<machinename> --time=<timestring (ex: 1d, none)>'
current_arg_index = 1
while current_arg_index < len(sys.argv):
    if sys.argv[current_arg_index].startswith('--machine'):
        arg = sys.argv[current_arg_index].split('=')
        current_machine = arg[1]
        print(f"Current machine identified as {current_machine} by command-line flag")
    elif sys.argv[current_arg_index].startswith('--time'):
        arg = sys.argv[current_arg_index].split('=')
        if arg[1] == 'none':
            time_filter_length = None
        elif not (arg[1].endswith('h') or arg[1].endswith('d') or arg[1].endswith('m')):
            print(f"Unrecognized time filter length: {arg[1]}")
            sys.exit(1)
        else:
            time_filter_length = arg[1]
    else:
        # handle generic args like user,
        arg = sys.argv[current_arg_index]
        if arg.startswith('--') and '=' in arg:
            print(f"Processing positional arg: {arg}")
            arg = arg.split('=')
            arg_name = arg[0][2:]
            if not arg_name in allowed_args:
                print(f"Argument not implemented: {arg}. Exiting.")
                sys.exit(1)
            command_line_filters[arg_name] = arg[1]
        else:
            print(f"Unrecognized argument: {arg}. Exiting.")
            sys.exit(1)
    current_arg_index += 1

if time_filter_length == None:
    time_filter = ''
else:
    time_filter = f"WHERE time >= now() - {time_filter_length} AND time <= now()"

################################################################################

# SELECT query #################################################################
running_query = f"SELECT test_id, slurm_jobid, username, app, test, machine, runtag, current_status, e_value FROM (SELECT test_id::field, job_id::field AS slurm_jobid, \"user\" AS username, app::tag, test::tag, machine::tag, runtag::tag, last(event_name::field) AS current_status, event_value::field AS e_value FROM events {time_filter} GROUP BY job_id) WHERE (current_status != 'check_end' AND (e_value = '0' OR e_value = '[NO_VALUE]')) OR current_status = 'job_queued'"
required_entries = ['slurm_jobid', 'test', 'app', 'test_id', 'runtag', 'machine', 'username']
################################################################################

# Global parameters extracted for ease of use ##################################
failed_job_event_name = 'check_end'  # Event name to log under for a failed job
failed_job_event_value = '2'   # This is the status logged for the event
success_job_event_name = 'check_end'  # Event name to log under for a completed job
success_job_event_value = '0'   # This is the status logged for the completed event

if 'RGT_SYSTEM_NAME' in os.environ and current_machine == 'unknown':
    current_machine = os.environ['RGT_SYSTEM_NAME']
    print(f"Current machine identified as {current_machine} by RGT_SYSTEM_NAME")
elif current_machine == 'unknown':
    print(f"This script requires RGT_SYSTEM_NAME to be set, or --machine=<machine> on the command-line.")
    sys.exit(1)


job_state_codes = {
    'fail': [ 'BOOT_FAIL', 'DEADLINE', 'FAILED', 'NODE_FAIL', 'OUT_OF_MEMORY', 'REVOKED', 'TIMEOUT' ],
    'success': ['COMPLETED'],
    'pending': ['PENDING', 'RUNNING']
}
################################################################################


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
        print(f"No Running tests found. Full response: {resp}")
        return []
    # each entry in series is a record
    col_names = resp['results'][0]['series'][0]['columns']
    values = resp['results'][0]['series'][0]['values']
    # Let's do the work of transforming this into a list of dicts
    ret_data = [ dict() for x in range(0, len(values)) ]
    for entry_index in range(0, len(values)):
        for c_index in range(0, len(col_names)):
            ret_data[entry_index][col_names[c_index]] = values[entry_index][c_index]
    return ret_data

def post_update_to_influx(d, failed=True):
    """ POSTs updated event to Influx """
    if failed:
        d['event_name'] = failed_job_event_name
        d['event_value'] = failed_job_event_value
    else:
        d['event_name'] = success_job_event_name
        d['event_value'] = success_job_event_value

    headers = {
        'Authorization': "Token " + influx_token,
        'Content-Type': "application/octet-stream",
        'Accept': "application/json"
    }
        #'Content-Type': "text/plain; charset=utf-8",
    if not 'timestamp' in d.keys():
        d['timestamp'] = datetime.datetime.now().isoformat()
    log_time = datetime.strptime(d['timestamp'], "%Y-%m-%dT%H:%M:%S")
    log_ns = int(datetime.timestamp(log_time) * 1000 * 1000 * 1000)

    influx_event_record_string = f'events,job_id={d["test_id"]},app={d["app"]},test={d["test"]},runtag={d["runtag"]},machine={d["machine"]} '
    nkeys = 0
    for key, value in d.items():
        if not key == 'timestamp':
            if nkeys > 0:
                influx_event_record_string += ','
            nkeys += 1
            influx_event_record_string += f"{key}=\"{value}\""
    influx_event_record_string += f' {str(log_ns)}'
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

def check_job_status(slurm_jobid):
    """
        Checks if a Slurm job is running by querying sacct
        Returns [False] (list length=1) or
            [JobID, Elapsed, Start, End, State, ExitCode, Reason, Comment]
    """
    sacct_format = 'JobID,Elapsed,Start,End,State%40,ExitCode,Reason%100,Comment%100'
    cmd=f'sacct -j {slurm_jobid} --format {sacct_format}'
    os.system(f'{cmd} 2>&1 | head -n 3 > {slurm_jobid}.tmp.txt')
    with open(f'{slurm_jobid}.tmp.txt', 'r') as f:
        line = f.readline()
        labels = line.split()
        comment_line = f.readline()   # line of dashes
        # use the spaces in the comment line to split the next line properly
        # a space indicates next field
        line = f.readline()
        fields = []
        search_pos = -1
        for i in range(0, len(labels)):
            next_space = comment_line.find(' ', search_pos + 1)
            cur_field = line[search_pos+1:next_space].strip()
            search_pos = next_space
            fields.append(cur_field)
    os.remove(f"{slurm_jobid}.tmp.txt")
    result = {}
    result['num_cols'] = len(labels)
    for i in range(0, len(labels)):
        result[labels[i].lower()] = fields[i]
    return result

def get_user_from_id(user_id):
    """ Given a user ID, return the username """
    # replace parenthesis with commas to make splitting easier
    os.system(f"id {user_id} 2>&1 | tr '()' '??' | cut -d'?' -f2 > tmp.user.txt")
    with open(f'tmp.user.txt', 'r') as f:
        user_name = f.readline().strip()
    if len(user_name) == 0:
        print(f"Couldn't find user name for {user_id}. Returning 'unknown'")
        user_name = 'unknown'
    os.remove(f"tmp.user.txt")
    return user_name

def check_data(entry):
    # Check if all required columns exist ######################################
    missing_entries = []
    for req in required_entries:
        if not req in entry:
            missing_entries.append(req)
    if len(missing_entries) > 0:
        return [ False, f"Missing entries: {','.join(missing_entries)}" ]
    # Check if the user matches ################################################
    if not entry['username'] == command_line_filters['user']:
        return [ False,
            f"Username of record ({entry['username']}) does not match requested user ({command_line_filters['user']})."]
    # Check if the app matches ################################################
    if 'app' in command_line_filters and not entry['app'] == command_line_filters['app']:
        return [ False,
            f"App of record ({entry['app']}) does not match requested app ({command_line_filters['app']})."]
    # Check if the runtag matches ##############################################
    if 'runtag' in command_line_filters and not entry['runtag'] == command_line_filters['runtag']:
        return [ False,
            f"Runtag of record ({entry['runtag']}) does not match requested runtag ({command_line_filters['runtag']})."]
    # Check if the test matches ##################################################
    if 'test' in command_line_filters and not entry['test'] == command_line_filters['test']:
        return [ False,
            f"Test of record ({entry['test']}) does not match requested test ({command_line_filters['test']})."]
    # End checks
    return [True, '']


data = query_influx_running()

for entry in data:
    # check to see if this entry should be parsed
    should_check, reason = check_data(entry)
    if not should_check:
        print(f"Skipping {entry['test_id']}. {reason}.")
        continue

    print(f"Processing {entry['test_id']}, SLURM id {entry['slurm_jobid']} ========================")
    job_status = check_job_status(entry['slurm_jobid'])

    if not job_status['num_cols'] == 8:
        print(f"Invalid query returned no data for job {entry['slurm_jobid']}. {job_status['num_cols']} columns. Skipping.")
        continue

    d = {
        'test_id': entry['test_id'],
        'machine': entry['machine'],
        'app': entry['app'],
        'test': entry['test'],
        'runtag': entry['runtag'],
        'job_id': entry['slurm_jobid']
    }

    if job_status['state'] in job_state_codes['fail']:
        print(f"Found failed job {d['job_id']}. Sending status to Influx.")
        d['timestamp'] = job_status['end']
        d['reason'] = f"Job exited in state {job_status['state']} at {job_status['end']}, after running for {job_status['elapsed']}."
        d['reason'] += f" Exit code: {job_status['exitcode']}, reason: {job_status['reason']}."
        d['comment'] = job_status['comment']
        post_update_to_influx(d)
    elif job_status['state'].startswith('CANCELLED'):
        print(f"Found user-cancelled job {d['job_id']}. Sending status to Influx.")
        d['timestamp'] = job_status['end']
        d['comment'] = job_status['comment']
        job_status_long = job_status['state'].split(' ')
        if len(job_status_long) > 1:
            cancel_user = get_user_from_id(job_status_long[2])
            d['reason'] = f" Job canceled at {job_status['end']} by {cancel_user}"
        else:
            d['reason'] = f"Job cancelled at {job_status['end']}"
        d['reason'] += f", after running for {job_status['elapsed']}."
        d['reason'] += f" Exit code: {job_status['exitcode']}, reason: {job_status['reason']}."
        post_update_to_influx(d)
    elif job_status['state'] in job_state_codes['success']:
        print(f"Marking job as completed: {d['job_id']}")
        d['timestamp'] = job_status['end']
        post_update_to_influx(d, failed = False)
    elif job_status['state'] in job_state_codes['pending']:
        print(f"Job {d['job_id']} is still pending. No action is being taken.")
    else:
        print(f"Unrecognized job state: {job_status['state']}. No action is being taken.")

sys.exit(0)
