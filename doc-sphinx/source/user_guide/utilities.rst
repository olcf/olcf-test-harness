=============
OTH Utilities
=============

.. toctree::
   :maxdepth: 1

The OLCF Test Harness (OTH) packages several scripts that may be useful in the course of testing.
For example, many of these scripts handle keeping the remote database up-to-date with current runs, in the event of job timeouts, connectivity issues, or data loss.
These scripts are documented below.

``rgt_archive_utility.py``
========

The ``rgt_archive_utility.py`` script allows you to "archive" a test.
What "archive" actually means is it allows you to select when to keep or discard a test's build and work directories, and will copy the test into a single location on the file system, without needing sym-links between the Run_Archive and scratch areas.
This is useful for taking all tests older than 6 months and manipulating the directories so that the test is in a single directory, ready to be tarred and archived (if desired).
The ``--help`` message for the ``rgt_archive_utility.py`` script is provided below.

.. code-block::

    usage: rgt_archive_tests.py [-h] --path-to-tests PATH_TO_TESTS
                            --path-to-archive PATH_TO_ARCHIVE
                            [--starttime STARTTIME] [--endtime ENDTIME]
                            [--keep-workdir {ON_FAIL,ALWAYS,NEVER}]
                            [--keep-builddir {ON_FAIL,ALWAYS,NEVER}]
                            [--delete-scratch-dir] [--delete-run-dir]
                            [--users USERS [USERS ...]]
                            [--machines MACHINES [MACHINES ...]]
                            [--apps APPS [APPS ...]]
                            [--tests TESTS [TESTS ...]]
                            [--runtags RUNTAGS [RUNTAGS ...]] [--no-tqdm]
                            [--print-summary] [--force] [--compress]
                            [--limit LIMIT] [--stop-after STOP_AFTER]
                            [--loglevel {NOTSET,DEBUG,INFO,WARNING,ERROR,CRITICAL}]
                            [--logfile LOGFILE]

    Locates and archives tests, condensing test output into a simplified directory
    structure.

    optional arguments:
      -h, --help            show this help message and exit
      --path-to-tests PATH_TO_TESTS
                            Path to the application repository directories (ie, Path_to_tests).
      --path-to-archive PATH_TO_ARCHIVE
                            Path to the archive location.
      --starttime STARTTIME
                            Absolute start time. Format: YYYY-MM-DDTHH:MM.
      --endtime ENDTIME     Absolute end time. Format: YYYY-MM-DDTHH:MM.
      --keep-workdir {ON_FAIL,ALWAYS,NEVER}
                            Customize when to copy the work directory to archive
                            (default: ON_FAIL).
      --keep-builddir {ON_FAIL,ALWAYS,NEVER}
                            Customize when to copy the build directory to archive
                            (default: ON_FAIL).
      --delete-scratch-dir  DANGEROUS. If set, deletes the build and work
                            directories after archiving.
      --delete-run-dir      DANGEROUS. If set, deletes the Run_Archive and Status
                            directories after archiving.
      --users USERS [USERS ...]
                            Specifies one or more UNIX users to archive jobs for
                            (default: all).
      --machines MACHINES [MACHINES ...]
                            Specifies one or more machines to archive jobs for
                            (default: all).
      --apps APPS [APPS ...]
                            Specifies one or more apps to archive jobs for
                            (default: all).
      --tests TESTS [TESTS ...]
                            Specifies one or more tests to archive jobs for
                            (default: all).
      --runtags RUNTAGS [RUNTAGS ...]
                            Specifies one or more runtags to archive jobs for
                            (default: all). This filter supports regex.
      --no-tqdm             If set, disables using TQDM progress bars.
      --print-summary       If set, prints a summary of how many test instances
                            are archived for each app-test.
      --force               DANGEROUS. If set, will remove the archive of an
                            existing test if found, then re-archive.
      --compress            If set, tar's and gzip's the resulting archive directory.
      --limit LIMIT         Maximum number of tests to archive.
      --stop-after STOP_AFTER
                            Specify a number of hours after which to cleanly pause
                            archiving and exit.
      --loglevel {NOTSET,DEBUG,INFO,WARNING,ERROR,CRITICAL}
                            Specify verbosity
      --logfile LOGFILE     Name/location of the log file (default: archive.log).
                            Set to /dev/null to disable log file.


``update_databases.py``
========

The ``update_databases.py`` script retrieves all incomplete tests from the remote database (ie, an InfluxDB instance), and tries to determine if that test has completed, but did not log its completion message.
This script has support for the Slurm job scheduler, and will look for the job ID of the given test, to see if it completed.
If the job failed, this script will log a completion message to the database with information about how long the job ran, if it timed out, if it hit a node failure, etc..
The ``--help`` message for the ``update_databases.py`` script is provided below.
This script requires the same environment variables as the core harness requires to enable the database backend, as described in :ref:`_influxdb_event_logging`.

.. code-block::

    usage: update_databases.py [-h] [--time TIME] [--starttime STARTTIME]
                           [--endtime ENDTIME] [--user USER] --machine MACHINE
                           [--app APP] [--test TEST] [--runtag RUNTAG]
                           [--loglevel {NOTSET,DEBUG,INFO,WARNING,ERROR,CRITICAL}]
                           [--dry-run] [--build-timeout BUILD_TIMEOUT]

    Updates harness runs in database backends using event and Slurm data

    optional arguments:
    -h, --help            show this help message and exit
    --time TIME, -t TIME  How far back to look for jobs relative to now (ex: 1h, 2d).
    --starttime STARTTIME
                          Absolute start time. Format: YYYY-MM-DDTHH:MM:SSZ.
                          Overrides --time
    --endtime ENDTIME     Absolute end time. Format: YYYY-MM-DDTHH:MM:SSZ.
                          Should only be used with --starttime.
    --user USER, -u USER  Specifies the UNIX user to update jobs for.
    --machine MACHINE, -m MACHINE
                          Specifies the machine to look for jobs for. Setting a
                          wrong machine may lead to SLURM job IDs not being found.
    --app APP             Specifies the app to update jobs for.
    --test TEST           Specifies the test to update jobs for.
    --runtag RUNTAG       Specifies the runtag to update jobs for.
    --loglevel {NOTSET,DEBUG,INFO,WARNING,ERROR,CRITICAL}
                          Specify verbosity
    --dry-run             When set, prints messages to send to databases, but does not send them.
    --build-timeout BUILD_TIMEOUT
                          Number of hours after a build_start event before
                          logging a failed build_end event.


``add_comment_to_databases.py``
========

The ``add_comment_to_databases.py`` script adds a comment to a specific test instance in the remote database (ie, an InfluxDB instance).
The ``--help`` message for the ``add_comment_to_databases.py`` script is provided below.
This script requires the same environment variables as the core harness requires to enable the database backend, as described in :ref:`_influxdb_event_logging`.

.. code-block::

    usage: add_comment_to_databases.py [-h] [--time TIME] --testid TESTID
                                   [--loglevel {NOTSET,DEBUG,INFO,WARNING,ERROR,CRITICAL}]
                                   [--dry-run] --message MESSAGE
                                   [--event {logging_start,build_start,build_end,submit_start,submit_end,job_queued,binary_execute_start,binary_execute_end,check_start,check_end}]

    Add a comment to a specific test ID in the events database.

    optional arguments:
    -h, --help            show this help message and exit
    --time TIME           How far back to look for jobs relative to now (ex: 1h, 2d).
    --testid TESTID       Specifies the harness test id to update jobs for.
    --loglevel {NOTSET,DEBUG,INFO,WARNING,ERROR,CRITICAL}
                          Specify verbosity
    --dry-run             When set, prints messages to send to databases, but does not send them.
    --message MESSAGE     Comment to add to the record.
    --event {logging_start,build_start,build_end,submit_start,submit_end,job_queued,binary_execute_start,binary_execute_end,check_start,check_end}
                          Specifies the harness event to add the comment to.
                          Defaults to most recent event.

``report_to_databases.py``
========

The ``report_to_databases.py`` script enables you to further utilize a remote database to store custom, non-harness metrics.
The ``--help`` message for the ``report_to_databases.py`` script is provided below.
This script requires the same environment variables as the core harness requires to enable the database backend, as described in :ref:`_influxdb_event_logging`.

.. code-block::

    usage: report_to_databases.py [-h] [--time TIME] --keys KEYS --values VALUES
                              [--loglevel {NOTSET,DEBUG,INFO,WARNING,ERROR,CRITICAL}]
                              [--table_name TABLE_NAME] [--dry-run]

    Post a custom metric to Databases

    optional arguments:
    -h, --help            show this help message and exit
    --time TIME, -t TIME  Timestamp to post record as. Format: YYYY-MM-DDTHH:MM:SS[.MS][Z]
    --keys KEYS, -k KEYS  A set of comma-separated keys to identify your metric by. Ex: machine=frontier
    --values VALUES, -v VALUES
                          A set of comma-separated values to post. Ex:
                          value_a=1,value_b=2. These may or may not be quoted
    --loglevel {NOTSET,DEBUG,INFO,WARNING,ERROR,CRITICAL}
                          Specify verbosity
    --table_name TABLE_NAME
                          Specifies the name of the table (measurement) to post to.
    --dry-run             When set, print the message to the databases, but do not send.


