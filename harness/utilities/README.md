*************************************
OLCF Harness InfluxDB Utility Scripts
*************************************

Requirements
############

Environment
-----------

These scripts require that the OLCF harness module is loaded (module load olcf\_harness).
The scripts use the INFLUX\_TAGS and INFLUX\_FIELDS defined in
**harness/libraries/status_file.py** when handling records with InfluxDB.


harness\_keys.py
---------------

harness\_keys.py provides the URIs and tokens required for the code to communicate
with InfluxDB. There must be a variable named ``influx_keys``, which is a Python
``dict()``, containing one or more sub-dictionaries. Each sub-dictionary is contains
the POST and GET URIs, and the token for the InfluxDB server. These keywords are
critically important. GET is for Influx-V2 query endpoints (for Flux queries), while
GET-v1 is for the legacy InfluxQL query endpoint. An example is seen below,
where you have 2 InfluxDB servers you may want to communicate with, named
``dev`` and ``prod``::

    influx_keys = {
        'dev': {
            'POST': 'http://my.influx.server.dev.com/write?precision=ns',
            'GET': 'http://my.influx.server.com/api/v2/query?org=myorg',
            'GET-v1': 'http://my.influx.server.dev.com/query?pretty=true',
            'token': 'tok-dev.!123abc#'
        },
        'prod': {
            'POST': 'http://my.influx.server.com/write?precision=ns',
            'GET': 'http://my.influx.server.com/api/v2/query?org=myorg',
            'GET-v1': 'http://my.influx.server.com/query?pretty=true',
            'token': 'tok-!123abc#'
        }
    }

Each code contains the ``--db`` flag, which allows you to select the Influx server
by the key name in influx\_keys (``--db dev``). 'dev' is the default. Each script
may require any subset of these URLs. For example, the ``add_comment_to_influx.py``
script requires POST and GET-v1.


InfluxDB Scripts
################

All utility scripts use ``argparse`` to parse arguments, and should provide useful
descriptions for flags when using the ``-h`` flag.

add\_comment\_to\_influx.py
------------------------

This script adds a comment to an InfluxDB record. The default is to select the last
event from the given test ID, but the user can provide the event to log the comment
under. For example, ``--event build_end``, if you add a comment pertaining to the
build.

Usage::

    add_comment_to_influx.py [-h] --testid TESTID --message MESSAGE --db DB
                             --event {logging_start,build_start,build_end,submit_start,
                                       submit_end,job_queued,binary_execute_start,
                                       binary_execute_end,check_start,check_end}


change\_machine\_in\_influx.py
---------------------------

This script will DUPLICATE a record, and change the machine name. The intended
use of this script is to correct an incorrect machine name, or if  the machine
name gets set to ``[NO_VALUE]`` by some environment corruption. This will
happen if RGT\_MACHINE\_NAME is not set, which *should* never be the case.`

There is no way to permanently delete a record in InfluxDB. The old record will
persist.

Usage::

    change_machine_in_influx.py [-h] --testid TESTID --newmachine NEWMACHINE --db DB


report\_to\_influx.py
-------------------

This script POSTs records to an InfluxDB measurement (like a SQL table) for
arbitrary data. This script automatically attempts to detect numbers, which
must not be quoted when sending to InfluxDB. Mixing data types for fields
is not supported by InfluxDB. Use ``--nosend`` to verify.

Usage::

    report_to_influx.py [-h] [--time TIME] --keys KEYS --values VALUES
                           [--verbose VERBOSE] [--table_name TABLE_NAME] --db
                           DB [--nosend]

    optional arguments:
        -h, --help            show this help message and exit
        --time TIME, -t TIME     Timestamp to post record as.
                                 Format: YYYY-MM-DDTHH:MM:SS[.MS][Z]
        --keys KEYS, -k KEYS     A set of comma-separated keys to identify your metric
                                 by. Ex: value_a=1,value_b=2
        --values VALUES, -v VALUES
                                 A set of comma-separated values to post. Ex:
                                 value_a=1,value_b=2. These may or may not be quoted.
        --verbose VERBOSE        Increase verbosity.
        --table_name TABLE_NAME  Specifies the name of the table (measurement) to post to.
        --db DB                  Specifies the database to post metrics to.
        --nosend                 When set, print the message to InfluxDB, but do not send.


update\_runs\_from\_slurm.py
-------------------------

This script retrieves any tests from InfluxDB that are still **Running**.

Note: it may be best to run the harness with ``--mode influx_log`` before running this script,
to clear any jobs that have finished normally, but failed to log. This script is geared to
log jobs that were aborted, cancelled, or walltimed.

The logic to determine if a job is running is::

    (current_status != 'check_end' AND (event_value = '0' OR event_value = '[NO_VALUE]'))
    OR
    current_status = 'job_queued'

Then, the script sends a query to ``sacct`` on the current machine, with all the listed SLURM JobIDs,
and checks if the job is seen as Running or Pending by SLURM. If the job has finished, this script
will POST back to InfluxDB under the event_name **check_end**, with a field named **reason** that
explains how the job finished. This final event is posted using the timestamp from the SLURM database.

Usage::

    update_runs_from_slurm.py [-h] [--time TIME] [--starttime STARTTIME]
                                 [--endtime ENDTIME] [--user USER] --machine
                                 MACHINE [--app APP] [--test TEST]
                                 [--runtag RUNTAG] [--db DB]
                                 [--verbosity VERBOSITY] [--dry-run] [--force]

Note: SLURM does not provide times in the same granularity as Python, so less precision will be available,
and events could be out-of-order when ordering by time, in the case of a job that exited immediately.

