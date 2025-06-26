==========
Extensions
==========

.. toctree::
   :maxdepth: 1

Optional extensions have been developed for use with the OLCF Test Harness (OTH).
Extensions are enabled through environment variables and metadata files placed in the Run_Archive directory of a test launch.

Database Event Logging
======================

The OTH leaves behind status files containing event metadata like timestamp, filesystem paths for work, scratch and archive directories, test name, error code, etc.
This information can additionally be logged to a supported database.
The OTH currently provides support for InfluxDB and Kafka (with Druid database backend).
To enable InfluxDB, add the following variables to your environment (ie, **export** in **bash**):

.. hlist::
    :columns: 1

    * RGT_INFLUXDB_URI : the URL for your InfluxDB instance (ie, ``https://my-influxdb.domain.com/api/v2/write?org=my-org&bucket=my-bucket&precision=ns``)
    * RGT_INFLUXDB_TOKEN : the token for your InfluxDB instance

To enable Kafka, add the following variables to your environment (ie, **export** in **bash**):

.. hlist::
    :columns: 1

    * RGT_KAFKA_URI : the URL for your Kafka instance (ie, ``https://my-kafka.domain.com:22222``)
    * RGT_KAFKA_USERNAME : the username for your Kafka account
    * RGT_KAFKA_PASSWORD : the password for your Kafka account
    * RGT_KAFKA_EVENTS_TOPIC : the name of the topic to use for Events logging
    * RGT_KAFKA_SSL_CA_LOCATION : absolute path to the certificate authority file for the Kafka instance.
    * RGT_KAFKA_SSL_CERTIFICATE_LOCATION : absolute path to the certificate file for the Kafka instance.

Note that this is a minimal configuration.
Multiple InfluxDB or Kafka instances can be logged to by supplying a semicolon-separated list to each of the variables.
Please see :ref:`env_vars_ext` for the full list of database-related environment variables.

Events are logged using the following data as tags in the InfluxDB measurement:

.. hlist::
    :columns: 1

    * **time**
    * **runtag** : system log tag for this harness launch, equal to **RGT_SYSTEM_LOG_TAG**
    * **app** : name of the application
    * **test** : name of the test
    * **test_id** : test identifier of this test instance
    * **machine** : machine name, equal to **RGT_MACHINE_NAME**

Tags are a set of unique identifiers used by InfluxDB to index records.
If you write 2 records to InfluxDB using the same set of tags, only the most recent will be kept.
Kafka logs these data as well, but does not have the concept of a tag.
Each set of tags is associated with a set of fields.
Event fields logged to InfluxDB are:

.. hlist::
    :columns: 1

    * **build_directory** : path to the build directory
    * **run_archive** : path to the Run_Archive directory
    * **workdir** : path to the work directory for this test
    * **rgt_path_to_sspace** : path to the scratch space derived from the **RGT_PATH_TO_SSPACE** environment variable
    * **event_filename** : name of the event file that this information is mirrored in
    * **event_name** : name of the event (ie, 'build_start')
    * **event_subtype** : specifies whether the event is start/end
    * **event_time** : time of the event
    * **event_type** : type of the event (ie, 'build', 'binary_execute')
    * **event_value** : status code of the event. '0' indicates successful
    * **hostname** : hostname of the system that the event was run on
    * **job_account_id** : account ID used to submit the job to the scheduler
    * **job_id** : JobID referenced by the scheduler
    * **path_to_rgt_package** : path to the harness source code used
    * **rgt_system_log_tag** : log tag defined for this run (mirrors **runtag**, logged for InfluxDB only)
    * **user** : username of the user that launched the harness
    * **comment** : enables the user to log comments to specific events
    * **output_txt** : output of specific events mined from files (last 1 kB only)
    * **check_alias** : an optional extension - alpha-numeric supplement to **event_value**

These fields are largely self-explanatory, but additional details for **output_txt** are provided below.
**output_txt** is constructed for **build_end**, **submit_end**, **binary_execute_end**, and **check_end** events.
The harness searches for files of a specific naming convention when each of those events is encountered.
For **build_end**, the OTH reads the last 1 kB from *output_build.txt*, which is a file automatically created by the harness to store the output of the build process.
For **submit_end**, the OTH reads the *submit.err* file, which is also automatically created by the harness during job submission.
For **binary_execute_end**, the OTH looks for a file with the extension *.o${job_id}*, and reads the last 1 kB from that file.
This file is not automatically created by the harness.
For **check_end**, the OTH looks for a file named *output_check.txt*, which is automatically created by the harness to store output from the check script.


Logging application metrics to a database
=========================================

The OTH provides capability to log metrics from each test to InfluxDB and/or Kafka.
This extension is a great way to visualize performance of a certain test over time.
This requires that the database's event logging described above is enabled.

To enable this extension, simply create a file named *metrics.txt* in the Run_Archive directory of a test launch (ie, */Path/to/Tests/$app/$test/Run_Archive/$test_id/metrics.txt*).
For InfluxDB, no further steps are required to enable metrics logging.
For Kafka, you must also set the environment variable ``RGT_KAFKA_METRICS_TOPIC`` (or set **kafka_metrics_topic** in the *machine.ini* file).
This environment variable provides the Kafka topic for the harness to send metrics to.

The *metrics.txt* file must exist by the end of the **report_cmd** execution (**report_cmd** is defined in the test's *rgt_test_input.ini* file).
A common place to create *metrics.txt* is in the check script, **check_cmd**.
Each line of this file must conform to one of the following formats:

.. code-block::

    # Comment lines begin with hashtags
    metric_name_1=value_1
    metric_name_2 = value_2
    # It is not recommended to use spaces in metric names, but it is allowable
    metric name 3 = value_3
    metric_name_3\t=\tvalue_3

The OTH will log metric names to InfluxDB databases using the same tags as InfluxDB event logging uses.
Kafka does not have tags, but uses a fixed-column format to log the **test_id**, **app**, **test**, **runtag**, **machine**, **event_time**, **job_id**, **metric_name**, and **metric_value**, which requires one message per metric.
When at least 1 metric is defined, the OTH also automatically calculates the time between **build_start** and **build_end** events, and **binary_execute_start** and **binary_execute_end**.
These events are logged as **build_time** and **execution_time**, respectively.
If you're interested only in **build_time** and **execution_time**, have your check script create a dummy *metrics.txt* file with a line like ``dummy=1``.
Note that the correct computation of **execution_time**  requires proper placement of the *log_binary_execution_time.py* calls in the job script,
since **execution_time** is the difference in time between the two *log_binary_execution_time.py* calls.


Monitoring the health of individual nodes
=========================================

In many-node systems, it can be very difficult to monitor the health of each node.
To address this, the OTH supports sending the status of each node to a database.
Similar to metrics logging, this extension requires that database's event logging is enabled, and this extension is triggered by the presence of a *nodecheck.txt* file in the Run_Archive directory of a test launch.
For Kafka, similar to metrics, the environment variable ``RGT_KAFKA_NODE_HEALTH_TOPIC`` is required (or set **kafka_node_health_topic** in the *machine.ini* file).
This extension also requires geospatial information about the node, by default.
This is discussed later in this section.
Each line of *nodecheck.txt* must have the following format:

.. code-block::

    # Comment lines begin with hashtags
    # Format: <nodename> <status> <message>
    Node1 PASS Some optional message that can have any number of spaces in it to associate with Node1
    Node2 FAIL optional message to associate with Node2
    Node3 HW-FAIL optional messaging to associate with Node3

The second column has a defined set of possible values, which are reduced to 4 common strings for usability in the database and dashboards.
Each status in *nodecheck.txt* must be a status present in the square braces for one of the 4 common statuses.
These values are:

#. FAILED : ['FAILED', 'FAIL', 'BAD']
#. SUCCESS : ['SUCCESS', 'OK', 'GOOD', 'PASS', 'PASSED']
#. HW-FAIL : ['INCORRECT', 'HW-FAIL']
#. PERF-FAIL : ['PERF', 'PERF-FAIL']

So to classify a successful test on a node, the line in *nodecheck.txt* may use *SUCCESS*, *OK*, *GOOD*, *PASS*, or *PASSED* keywords, and these are not case-sensitive, so *success* also works.

These 4 values are intended to present a known set of statuses to the InfluxDB database and dashboards, for ease of visualization.
``FAILED``, ``SUCCESS``, and ``PERF-FAIL`` are self-explanatory.
``HW-FAIL`` is intended to be a status associated with a hardware failure (ie, bus errors, power fault, network failure).

This extension logs results to the **node_health** measurement (table) of InfluxDB using **machine**, **node**, and **test** as tags.
Kafka logs the same test information that it does for metrics: **test_id**, **app**, **test**, **runtag**, **machine**, **event_time**, and **job_id**.
By default, this extension also requires geospatial information about each node (ie, cabinet number, board number, row number).
For Kafka, due to fixed-column formatting requirements, the only acceptable/required geospatial metadata is **xname**, which typically encodes the cabinet, board, and row numbers in a single string, e.g. ``a36n21``.
InfluxDB allows for flexible-column formatting, so any number of geospatial metadata may be provided.
To bypass this feature (common for single-cabinet systems), set the **RGT_NODE_LOCATION_FILE** environment variable to ``none`` (not case-sensitive).
To utilize this feature, provide the absolute path to a JSON file containing the desired information by using the **RGT_NODE_LOCATION_FILE** environment variable.
An example portion from this file may look like:

.. code-block::

    {
        "node001": {
            "cabinet": "x0",
            "switch": "c0",
            "slot": "s0",
            "xname": "x0c0s0"
        },
        "node002": {
            "cabinet": "x0",
            "switch": "c0",
            "slot": "s1"
            "xname": "x0c0s1"
        },
        ...
    }


This information is then available when querying the database.

Check Alias
===========

Check aliasing allows codes to provide an alpha-numeric explanation to the check script exit code.
For example, the OTH uses a **check_end** event value of ``1`` to dictate a failure.
Failures come in many shapes and sizes, so an example of how you would use a check alias is by having distinct values such as ``MPI_ERR``, ``BUS_ERR``, ``TIMEOUT``, ``INPUT_ERR``.
This simply supplies an alphabetic dimension to categorizing failures.

To enable this extension, create a file named *check_alias.txt* in the Run_Archive directory of a test launch (ie, */Path/to/Tests/$app/$test/Run_Archive/$test_id/check_alias.txt*).
**check_alias** is set to the content of the first line of this file.
This **check_alias** field is set in each event file, so InfluxDB is not required for this extension.
**check_alias** is sent to databases alongside the standard event metadata, if any databases are enabled.


