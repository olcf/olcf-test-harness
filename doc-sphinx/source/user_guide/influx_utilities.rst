=============================
OTH-provided Influx Utilities
=============================


This page describes the use cases for the utility scripts
provided in ``olcf-test-harness/harness/utilities``.


update_runs_from_slurm.py
-------------------------

Goal
^^^^

The goal of this script is to update InfluxDB using
data from the SLURM workload manager to update tests
that have failed or aborted, causing events to not
be logged to InfluxDB.

Requirements
^^^^^^^^^^^^

This script requires a file named ``harness_keys.py``, which contains
the following variables declared at the global level:

#. post_influx_uri: the URL for POST requests for the InfluxDB server.
   Example: ``https://my.influx.server/api/v2/write?org=accept&bucket=accept&precision=ns``.
#. get_influx_uri: the URL for GET requests for the InfluxDB server.
   Example: ``https://my.influx.server/api/v2/query?pretty=true``.
#. influx_token: token for the InfluxDB server.

Details
^^^^^^^

This file fetches all instances that meet the following
criteria from InfluxDB:

#. The last recorded harness event is not *check_end*
#. The last event value is *0* or *[NO_VALUE]*, or is *job_queued*

A test instance that meets this criteria is classified as
*Running*.
This script then checks each instance for a series of criteria such as:

#. Does the current user match the user that submitted this instance?
#. Is the current machine the same as the instance?

The script also provides flags to filter further for specifying
the app, test, and runtag of instances to check. Run
``./update_runs_from_slurm.py help`` for a full list of parameters.

Once a run has passed these criteria, the script
fetches information about the SLURM job ID of this run via ``sacct``.
Based on the state reported by ``sacct``, the script will send a
*check_end* event with event value *2* to Influx, if the run failed.
This script also compiles information about this failure from ``sacct``
fields such as *Reason* or *Comment*, and sends them in a field
named *Reason* to Influx.


report_to_influx.py
-------------------

Goal
^^^^

This script is designed to extract the functionality for sending
data to InfluxDB into a simple-to-use command-line app.
Given a number of tags and key-value pairs, and valid Influx URI
and token, this script logs the key-value pairs to an InfluxDB
measurement named *non_harness_values*. This simply extends the
usage of InfluxDB beyond the OTH harness.

Requirements
^^^^^^^^^^^^

This script requires a file named ``harness_keys.py``, which contains
the following variables declared at the global level:

#. influx_keys: a Python Dict object containing 1 or more entries. Each key should be the name
   of an InfluxDB instance. For example, if you have production and development version of
   InfluxDB, you might have:

   .. code-block:: python

     influx_keys = {
        'dev': ["https://my.influx.server.development/api/v2/write?org=accept&bucket=accept&precision=ns",
                "mydevservertoken"],
        'prod': ["https://my.influx.server/api/v2/write?org=accept&bucket=accept&precision=ns",
                "myprodservertoken"]
     }

