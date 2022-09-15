#!/usr/bin/env python3

################################################################################
# Author: Nick Hagerty
# Date modified: 07-15-2022
################################################################################
# Purpose:
#   Provides a utility to log any data to InfluxDB for viewing in Grafana.
#   This submits data to a separate source from the harness metrics and events,
#   So the data will not become mixed.
################################################################################
# Pre-requirements:
#   Must add a file named harness_keys.py that contains a dictionary named
#   influx_keys, containing entries in the format:
#       'instance_name': ['instance_uri', 'instance_token']
#   where instance_name matches the argument of --version (default 'dev')
################################################################################

import os
import requests
import subprocess
import sys
from harness_keys import influx_keys

class InfluxReport:
    def __init__(self, d):
        if not 'keys' in d.keys():
            print(f"No keys provided. Please provide at least one key")
        if not 'values' in d.keys():
            print(f"No values provided. Please provide at least one value")

        self.headers = {
            'Authorization': "Token " + d['token'],
            'Content-Type': "text/plain; charset=utf-8",
            'Accept': "application/json"
        }
        self.influx_uri = d['uri']
        # d['keys'] = ['key1=value1', 'key2=value2',...]
        self.keys = d['keys']
        # d['values'] = ['value1=v1', 'value2=v2',...]
        self.values = d['values']

    def send(self):
        influx_event_record_string = f"non_harness_values,{','.join(self.keys)}"
        num_metrics = len(self.values)
        influx_event_record_string += f" {','.join(self.values)}"
        try:
            r = requests.post(self.influx_uri, data=influx_event_record_string, headers=self.headers)
            print(f"Successfully sent {influx_event_record_string} to {self.influx_uri}")
            return 0
        except requests.exceptions.ConnectionError as e:
            print("InfluxDB is not reachable. Request not sent.")
            return 1
        except Exception as e:
            print(f"Failed to send {influx_event_record_string} to {self.influx_url}:")
        return 2


def print_usage():
    print("Usage: ./report_to_influx.py [args]")
    print("\t--keys <keys>       (ex: machine=crusher,purpose=testing,...)")
    print("\t\tKeys allow you to select your entry in InfluxDB - ie, by machine name and test name. These are like primary keys in SQL.")
    print("\t\tPreferred keys are machine and purpose. For example, --keys machine=crusher,purpose=job_monitor")
    print("\t--values <values>   (ex: jobs_in_queue=1,nodes_running=1,...)")
    print("\t--db <name>    Sends data to a named instance of InfluxDB. This should match the key name in the uri and token dicts. Default: dev")

if len(sys.argv) < 2:
    print_usage()
    sys.exit(0)

d = {}
d['uri'] = influx_keys['dev']['POST']
d['token'] = influx_keys['dev']['token']

index = 1
nargs = len(sys.argv)
while index < nargs:
    if sys.argv[index] == "--keys":
        index += 1
        k = sys.argv[index].split(',')
        d['keys'] = k
    elif sys.argv[index] == "--values":
        index += 1
        v = sys.argv[index].split(',')
        d['values'] = v
    elif sys.argv[index] == "--db":
        index += 1
        if not sys.argv[index] in influx_keys.keys():
            print(f"Could not find key: {sys.argv[index]} in influx_keys")
            sys.exit(1)
        elif not ('POST' in influx_keys[sys.argv[index]] and 'token' in influx_keys[sys.argv[index]]):
            print(f"Could not find POST and token in influx_keys for {sys.argv[index]}")
            sys.exit(1)
        d['uri'] = influx_keys[sys.argv[index]]['POST']
        d['token'] = influx_keys[sys.argv[index]]['token']
    else:
        print(f"Unrecognized kwarg: {sys.argv[index]}")
        print_usage()
        sys.exit(1)
    index += 1

ir = InfluxReport(d)
ex_code = ir.send()
sys.exit(ex_code)
