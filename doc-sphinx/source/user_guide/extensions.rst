===================================
Extensions to the OLCF Test Harness
===================================

.. toctree::
   :maxdepth: 1

Optional extensions have been developed for use with the OLCF Test Harness (OTH).
Extensions are enabled through environment variables and metadata files placed in the Run_Archive directory of a test launch.


InfluxDB Event Logging
======================

The OTH leaves behind event information in files on the file system, with data like timestamp, path to tests, test name, etc.
This information can additionally be logged to an InfluxDB time series database.
To enable this extension, add the following variables to your environment (ie, ``export`` in ``bash``):

* RGT_INFLUX_URI : the URL (with appropriate endpoint) for your InfluxDB instance (ie, ``https://my-influxdb.domain.com/api/v2/write?org=my-org&bucket=my-bucket&precision=ns``)
* RGT_INFLUX_TOKEN : the token for your InfluxDB instance

Note that the ``RGT_INFLUX_URI`` contains information such as the organization name, bucket name, and desired precision.
Currently the OTH only supports nanosecond precision.

Events are logged using the following data as tags in the InfluxDB measurement:

* time
* runtag : system log tag for this harness launch. Equal to ``RGT_SYSTEM_LOG_TAG``, if that environment variable is set.
* app : name of the application
* test : name of the test
* test_id : test identifier of this test instance
* machine : machine name

Tags are a set of unique identifiers.
If you write 2 records to InfluxDB using the same set of tags, only the most recent will be kept.
Each set of tags is associated with a set of fields.
Event fields logged to InfluxDB are:

* build_directory : path to the build directory
* run_archive : path to the Run_Archive directory
* workdir : path to the work directory for this test
* rgt_path_to_sspace : path to the scratch space provided by the ``RGT_PATH_TO_SSPACE`` environment variable
* event_filename : name of the event file that this information is mirrored in
* event_name : name of the event (ie, 'build_start')
* event_subtype : specifies whether the event is start/end
* event_time : time of the event
* event_type : type of the event (ie, 'build', 'binary_execute')
* event_value : status code of the event. '0' indicates successful
* hostname : hostname of the system that the event was run on
* job_account_id : account ID used to submit the job to the scheduler
* job_id : JobID referenced by the scheduler
* path_to_rgt_package : path to the harness source code used
* rgt_system_log_tag : log tag defined for this run (mirrors ``runtag``)
* test_instance : a string set to "$app,$test,$test_id"
* user : username of the user that launched the harness
* comment : enables the user to log comments to specific events
* reason : used by some harness utility scripts to log explanations to InfluxDB, such as node failure messages
* output_txt : output of specific events mined from files (last 64 kB only).
* check_alias : an optional extension on InfluxDB

These fields are largely self-explanatory, but additional details for ``output_txt`` are provided below.
``output_txt`` is mined for ``build_end``, ``submit_end``, ``binary_execute_end``, and ``check_end`` events.
The harness searches for files of a specific naming convention when each of those events is encountered.
For ``build_end``, the OTH reads the last 64 kB from ``output_build.txt``, which is a file automatically created by the harness to store the output of the build process.
For ``submit_end``, the OTH reads the ``submit.err`` file, which is also automatically created by the harness during job submission.
For ``binary_execute_end``, the OTH looks for a file with the extension ``.o${job_id}``, and reads the last 64 kB from that file.
This file is not automatically created by the harness.
For ``check_end``, the OTH looks for a file named ``output_check.txt``, which is automatically created by the harness to store output from the check script.


Logging application metrics to InfluxDB
=======================================

The OTH provides capability to log metrics from each test instance to InfluxDB.
This extension is a great way to visualize performance of a certain test over time.
This requires that InfluxDB event logging is enabled.

To enable this extension, simply create a file named ``metrics.txt`` in the Run_Archive directory of a test launch (ie, ``/Path/to/Tests/$app/$test/Run_Archive/$test_id/metrics.txt``).
Each line of this file must conform to one of the following formats:

.. text::

    # Comment lines begin with hashtags
    metric_name_1=value_1
    metric_name_2 = value_2
    # It is not recommended to use spaces in metric names, but it is allowable
    metric name 3 = value_3
    metric_name_3\t=\tvalue_3

This file must exist on the file system by the end of the reporting script.
Then, the OTH will log metric names to the InfluxDB database using the same tags as InfluxDB event logging uses.
When at least 1 metric is defined, the OTH also automatically calculates the time between ``build_start`` and ``build_end`` events, and ``binary_execute_start`` and ``binary_execute_end``.
These events are logged as ``build_time`` and ``execution_time``.
If you're interested only in ``build_time`` and ``execution_time``, have your check script create a dummy ``metrics.txt`` file with a line like ``dummy=1``.
Note that this requires proper placement of the ``log_binary_execution_time.py`` calls in the job script.


Monitoring the health of many nodes
===================================

In many-node systems, it can be very difficult to monitor the health of specific nodes.
To address this, the OTH supports a node-focused monitoring process.
Similar to metrics logging, this extension requires that InfluxDB event logging is enabled, and this extension is triggered by the presence of a ``nodecheck.txt`` file in the Run_Archive directory of a test launch.
This extension also requires geospatial information about the node, by default.
This is discussed later in this section.
Each line of ``nodecheck.txt`` must have the following format:

.. text::

    # Comment lines begin with hashtags
    Node1 PASS Some optional message that can have any number of spaces in it to associate with Node1
    Node2 FAIL optional message to associate with Node2
    Node3 HW-FAIL optional messaging to associate with Node3

The second column has a defined set of possible values, which are reduced to 4 common statuses for usability in the database and dashboards.
These values are:

1. FAILED : ['FAILED', 'FAIL', 'BAD']
2. SUCCESS : ['SUCCESS', 'OK', 'GOOD', 'PASS', 'PASSED']
3. HW-FAIL : ['INCORRECT', 'HW-FAIL']
4. PERF-FAIL : ['PERF', 'PERF-FAIL']

These 4 values are intended to present a known set of statuses to the InfluxDB database and dashboards, for ease of visualization.
``HW-FAIL`` is intended to be a status associated with a hardware failure (ie, bus errors, GPU power fault, network failure).

This extension logs results to the ``node_health`` measurement (table) of InfluxDB using ``machine``, ``node``, and ``test`` as tags.
By default, this extension also requires geospatial information about each node (ie, cabinet number, board number, row number).
This information is used as an InfluxDB tag to identify each record and provide the capability to correlate failures by location.
To bypass this (for smaller systems, especially), set the ``RGT_IGNORE_NODE_LOCATION`` to any value in your environment.
To utilize this feature, provide the absolute path to a JSON file containing the desired information by using the ``RGT_NODE_LOCATION_FILE`` environment variable.
An example snippet from this file may look like:

.. text::

    {
        "node001": {
            "cabinet": "c0",
            "switch": "s0",
            "slot": "s0"
        },
        "node002": {
            "cabinet": "c0",
            "switch": "s0",
            "slot": "s1"
        },
        ...
    }


Then, when querying InfluxDB in this example, you may use ``cabinet``, ``switch``, and ``slot`` to select the nodes to view.

