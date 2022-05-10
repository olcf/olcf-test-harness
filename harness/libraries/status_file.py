#! /usr/bin/env python3
"""
-------------------------------------------------------------------------------
File:   status_file.py
Author: Arnold Tharrington (arnoldt@ornl.gov)
National Center for Computational Sciences, Scientific Computing Group.
Oak Ridge National Laboratory
Copyright (C) 2015 Oak Ridge National Laboratory, UT-Battelle, LLC.
-------------------------------------------------------------------------------
"""

import os
import datetime
import re
import socket
import pprint
import abc
import requests
import urllib
import glob
import dateutil.parser


from libraries.layout_of_apps_directory import apptest_layout

class StatusFile:
    """Perform operations pertaining to logging the status of jobs."""

    ###################
    # Class variables #
    ###################


    # Header lines for status.
    STATUS_COLUMN_START  = 'Start Time'
    STATUS_COLUMN_LAUNCH = 'Launch ID'
    STATUS_COLUMN_UNIQUE = 'Unique ID'
    STATUS_COLUMN_COUNT  = 'Run Count'
    STATUS_COLUMN_BATCH  = 'Batch Job ID'
    STATUS_COLUMN_BUILD  = 'Build Status'
    STATUS_COLUMN_SUBMIT = 'Submit Status'
    STATUS_COLUMN_CHECK  = 'Check Status'

    STATUS_COLUMNS = {
        STATUS_COLUMN_START  : 0,
        STATUS_COLUMN_LAUNCH : 1,
        STATUS_COLUMN_UNIQUE : 2,
        STATUS_COLUMN_COUNT  : 3,
        STATUS_COLUMN_BATCH  : 4,
        STATUS_COLUMN_BUILD  : 5,
        STATUS_COLUMN_SUBMIT : 6,
        STATUS_COLUMN_CHECK  : 7
    }


    __LINE_FORMAT = "%-28s %-50s %-20s %-10s %-20s %-15s %-15s %-15s\n"
    spaces_header = __LINE_FORMAT % (' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ')
    hashes_header = str.replace(spaces_header, ' ', '#')
    column_header = __LINE_FORMAT % (f'# {STATUS_COLUMN_START}', STATUS_COLUMN_LAUNCH,
                                     STATUS_COLUMN_UNIQUE, STATUS_COLUMN_COUNT, STATUS_COLUMN_BATCH,
                                     STATUS_COLUMN_BUILD, STATUS_COLUMN_SUBMIT, STATUS_COLUMN_CHECK)
    header =  hashes_header
    header += spaces_header
    header += column_header
    header += spaces_header
    header += hashes_header

    # Name of the input file.
    FILENAME = apptest_layout.test_status_filename
    """str: The filename of the subtest status file."""

    COMMENT_LINE_INDICATOR = '#'
    """str: The comment character for the subtest status file."""

    #---Event identifiers.

    EVENT_LOGGING_START = 'LOGGING_START'
    EVENT_BUILD_START = 'BUILD_START'
    EVENT_BUILD_END = 'BUILD_END'
    EVENT_SUBMIT_START = 'SUBMIT_START'
    EVENT_SUBMIT_END = 'SUBMIT_END'
    EVENT_JOB_QUEUED = 'JOB_QUEUED'
    EVENT_BINARY_EXECUTE_START = 'BINARY_EXECUTE_START'
    EVENT_BINARY_EXECUTE_END = 'BINARY_EXECUTE_END'
    EVENT_CHECK_START = 'CHECK_START'
    EVENT_CHECK_END = 'CHECK_END'

    EVENT_LIST = [
        EVENT_LOGGING_START,
        EVENT_BUILD_START,
        EVENT_BUILD_END,
        EVENT_SUBMIT_START,
        EVENT_SUBMIT_END,
        EVENT_JOB_QUEUED,
        EVENT_BINARY_EXECUTE_START,
        EVENT_BINARY_EXECUTE_END,
        EVENT_CHECK_START,
        EVENT_CHECK_END]

    EVENT_DICT = {
        EVENT_LOGGING_START:
            ['Event_110_logging_start.txt', 'logging', 'start'],
        EVENT_BUILD_START:
            ['Event_120_build_start.txt', 'build', 'start'],
        EVENT_BUILD_END:
            ['Event_130_build_end.txt', 'build', 'end'],
        EVENT_SUBMIT_START:
            ['Event_140_submit_start.txt', 'submit', 'start'],
        EVENT_SUBMIT_END:
            ['Event_150_submit_end.txt', 'submit', 'end'],
        EVENT_JOB_QUEUED:
            ['Event_160_job_queued.txt', 'job', 'queued'],
        EVENT_BINARY_EXECUTE_START:
            ['Event_170_binary_execute_start.txt', 'binary_execute', 'start'],
        EVENT_BINARY_EXECUTE_END:
            ['Event_180_binary_execute_end.txt', 'binary_execute', 'end'],
        EVENT_CHECK_START:
            ['Event_190_check_start.txt', 'check', 'start'],
        EVENT_CHECK_END:
            ['Event_200_check_end.txt', 'check', 'end']
    }

    #---Field identifiers.

    FIELDS_PER_TEST_INSTANCE = [
        'rgt_system_log_tag',
        'user',
        'hostname',
        'job_account_id',
        'rgt_path_to_sspace',
        'path_to_rgt_package',
        'build_directory',
        'workdir',
        'run_archive',
        'cwd',
        'app',
        'test',
        'test_id',
        'test_instance']

    FIELDS_PER_EVENT = [
        'job_id',
        'event_filename',
        'job_status',
        'runtag',
        'event_time',
        'event_name',
        'event_type',
        'event_subtype',
        'event_value']

    FIELDS_SPLUNK_SPECIAL = ['job_status', 'event_value']

    NO_VALUE = '[NO_VALUE]'

    #-----------------------------------------------------
    #                                                    -
    # Start of section for StatusFiles modes.            -
    #                                                    -
    #-----------------------------------------------------
    MODE_NEW = 'New'
    """str: Indicates that we logging a new subtest entry in the status file."""

    MODE_OLD = 'Old'
    """str: Indicates that we updating an old subtest entry in the status file."""

    #-----------------------------------------------------
    #                                                    -
    # End of section for StatusFiles modes.              -
    #                                                    -
    #-----------------------------------------------------

    #-----------------------------------------------------
    #                                                    -
    # Standard values for test results of the status file-
    #                                                    -
    #-----------------------------------------------------
    PENDING = "-1"
    PASS = "0"
    FAIL = "1"
    PLACE_HOLDER = r"***"
    #-----------------------------------------------------
    #                                                    -
    # End of section for standard values of the          -
    # status file.                                       -
    #                                                    -
    #                                                    -
    #-----------------------------------------------------

    #-----------------------------------------------------
    #                                                    -
    # Values for the build results in the status file.   -
    #                                                    -
    #-----------------------------------------------------
    BUILD_RESULTS = {"Pending" : PENDING,
                     "Pass" : PASS,
                     "Failure" : FAIL}
    #-----------------------------------------------------
    #                                                    -
    # End of section for values for the build results in -
    # the status file.                                   -
    #                                                    -
    #-----------------------------------------------------

    #-----------------------------------------------------
    #                                                    -
    # Values for the submit results in the status file.  -
    #                                                    -
    #-----------------------------------------------------
    SUBMIT_RESULTS = {"Pending" : PENDING,
                      "Pass" : PASS,
                      "Failure" : FAIL}
    #-----------------------------------------------------
    #                                                    -
    # End of section for values for the submit results   -
    # in the status file.                                -
    #                                                    -
    #-----------------------------------------------------

    #-----------------------------------------------------
    #                                                    -
    # Values for the correct results in the status file. -
    #                                                    -
    #-----------------------------------------------------
    CHECK_RESULTS = {"Pending" : PENDING,
                     "In progress" : 17,
                     "Pass" : PASS,
                     "Failure" : FAIL,
                     "Performance failure" : 5}
    #-----------------------------------------------------
    #                                                    -
    # End of section for values for the correct results  -
    # in the status file.                                -
    #                                                    -
    #-----------------------------------------------------

    #################
    # Class methods #
    #################

    @staticmethod
    def ignore_line(line):
        """Indicate whether parser should ignore a line (e.g., is comment)."""
        result = False

        tmpline = line.strip()

        if len(tmpline) > 0:
            if tmpline[0] == StatusFile.COMMENT_LINE_INDICATOR:
                result = True
        else:
            result = True

        return result

    @classmethod
    def validate_mode(cls,mode):
        """Validates that we are using a valid mode."""
        if mode == cls.MODE_NEW :
            pass
        elif mode == cls.MODE_OLD:
            pass
        else:
            raise

    ###################
    # Special methods #
    ###################

    def __init__(self,logger,path_to_status_file):
        """Constructor.

        Parameters
        ----------
        path_to_status_file : str
            The fully qualified path to the subtest status file.

        """
        self.__logger = logger
        self.__job_id = None
        self.__test_id = None

        # The first task is set the path to status file.
        self.__status_file_path = path_to_status_file

        # The second task is to create the status file.
        self.__create_status_file(path_to_status_file)

    ###################
    # Public methods  #
    ###################

    @property
    def status_file_path(self):
        return self.__status_file_path

    def initialize_subtest(self, launch_id, unique_id):
        """Initializes a new entry to the status file.

        Parameters
        ----------
        unique_id : str
            The unique is for the subtest.
        """

        self.__test_id = unique_id
        if self._subtest_already_initialized(unique_id):
            pass
        else:
            event_time = self.log_event(StatusFile.EVENT_LOGGING_START)
            self.__status_file_add_test_instance(event_time, launch_id, unique_id)
        return

    def getLastHarnessID(self):
        """Returns the last harness ID of the subtest status file.

        If there are no entries, then None is returned. If the
        status file doesn\'t exist then an error is raised.

        Returns
        -------
        str
            The harness id of the latest entry in the subtest status file.
        """
        with open(self.__status_file_path, "r") as file_obj:
            records = file_obj.readlines()

        line = records[-1]
        words = line.rstrip().split()
        unique_col = StatusFile.STATUS_COLUMNS[StatusFile.STATUS_COLUMN_UNIQUE]
        if len(words) > unique_col:
            subtest_harness_id = words[unique_col]
        else:
            subtest_harness_id = None
        return subtest_harness_id

    def log_event(self, event_id, event_value=NO_VALUE):
        """Log the occurrence of a harness event.
           This version logs a predefined event specified in the EVENT_DICT dictionary.
        """

        if event_id in StatusFile.EVENT_DICT:
            event_filename = StatusFile.EVENT_DICT[event_id][0]
            event_type = StatusFile.EVENT_DICT[event_id][1]
            event_subtype = StatusFile.EVENT_DICT[event_id][2]
        else:
            print('Warning: event not recognized. ' + event_id)
            event_filename = 'Event__UNKNOWN_EVENT_ENCOUNTERED_'
            event_type = ''
            event_subtype = ''

        return self.__log_event(event_id, event_filename,
                                event_type, event_subtype, str(event_value))


    def log_custom_event(self, event_type, event_subtype, event_value=NO_VALUE):
        """Log the occurrence of a harness event.
           This version logs a custom user event not in the dictionary.
        """

        event_name = (event_type + '_' + event_subtype
                      if event_type != '' and event_subtype != ''
                      else event_type + event_subtype)

        event_id = 'EVENT_CUSTOM'

        event_filename = 'Event_' + event_name + '.txt'

        return self.__log_event(event_id, event_filename,
                                event_type, event_subtype, str(event_value))

    def isTestFinished(self, subtest_harness_id):
        """Checks if the subtest of subtest_harness_id has completed.

        Parameters
        ----------
        subtest_harness_id : str
            The harness id of the subest that we wish to check.

        Returns
        -------
        bool
            If the subtest with subtest_harness_id is complete, then True is
            returned, otherwise False is returned.
        """
        # Get the corresponding record from the status file that
        # lists the test results for subtest_harness_id.
        record = self.__get_harness_id_record(subtest_harness_id)

        if record == None:
            test_finished = False
        else:
            # Strip line/record of all leading and trailing whitespace.
            record = record.strip()

            # If batch column, build column, submit column, or check column equals StatusFile.PLACE_HOLDER
            # then we are not finished. The test is still in progress.
            words = record.split()
            batch_col = StatusFile.STATUS_COLUMNS[StatusFile.STATUS_COLUMN_BATCH]
            tmp_words = words[batch_col:]
            if tmp_words.count(StatusFile.PLACE_HOLDER) >= 1:
                test_finished = False
            else:
                # The check column must indicate that the test is no longer pending and not in progress.
                check_col = StatusFile.STATUS_COLUMNS[StatusFile.STATUS_COLUMN_CHECK]
                check_val = int(words[check_col])
                if (check_val  > int(StatusFile.CHECK_RESULTS["Pending"]) and
                    check_val != int(StatusFile.CHECK_RESULTS["In progress"])):
                    test_finished = True
                else:
                    test_finished = False

        return test_finished

    def didAllTestsPass(self):
        """ Checks if all tests have passed.

        Returns
        -------
        bool
            A True value is returned when all tests have passed. Explicitly stated, this
            means all tests have 0's for build, submit, and correct results. Otherwise a
            False value is returned.
        """
        ret_value = True

        with open(self.__status_file_path, 'r') as status_file_obj:
            records = status_file_obj.readlines()

        verify_test_passed = lambda a_list : True if a_list.count(StatusFile.PASS) == 3 else False

        build_col = StatusFile.STATUS_COLUMNS[StatusFile.STATUS_COLUMN_BUILD]

        for index, line in enumerate(records):
            if self.ignore_line(line):
                continue

            words = line.rstrip().split()
            tmp_words = words[build_col:]

            ret_value = ret_value and verify_test_passed(tmp_words)

        return ret_value

    ###################
    # Private methods #
    ###################
    def _subtest_already_initialized(self, unique_id):
        found_instance = False

        with open(self.__status_file_path, 'r') as status_file_obj:
            records = status_file_obj.readlines()

        unique_col = StatusFile.STATUS_COLUMNS[StatusFile.STATUS_COLUMN_UNIQUE]

        for index, line in enumerate(records):
            words = line.rstrip().split()

            if self.ignore_line(line):
                continue

            if len(words) > unique_col:
                test_id = words[unique_col]
                if test_id == unique_id:
                    found_instance = True
                    break

        return found_instance

    def __get_harness_id_record(self, harness_id):
        record = None
        with open(self.__status_file_path, 'r') as status_file_obj:
            records = status_file_obj.readlines()

        unique_col = StatusFile.STATUS_COLUMNS[StatusFile.STATUS_COLUMN_UNIQUE]

        for index, line in enumerate(records):
            if self.ignore_line(line):
                continue
            words = line.rstrip().split()
            if len(words) > unique_col:
                test_id = words[unique_col]
                if test_id == harness_id:
                    record = line
                    break

        return record

    def __get_all_harness_id(self):
        with open(self.__status_file_path, 'r') as status_file_obj:
            records = status_file_obj.readlines()

        unique_col = StatusFile.STATUS_COLUMNS[StatusFile.STATUS_COLUMN_UNIQUE]

        harness_ids = []
        for index, line in enumerate(records):
            if self.ignore_line(line):
                continue
            words = line.rstrip().split()
            if len(words) > unique_col:
                test_id = words[unique_col]
                harness_ids.append(test_id)

        return harness_ids

    def __log_event(self, event_id, event_filename, event_type, event_subtype,
                    event_value):
        """Official function to log the occurrence of a harness event.
        """

        # THE FOLLOWING LINE IS THE OFFICIAL TIMESTAMP FOR THE EVENT.
        event_time = datetime.datetime.now()
        event_time_unix = event_time.timestamp()
        event_time = event_time.isoformat()


        # THE FOLLOWING FORMS THE OFFICIAL TEXT DESCRIBING THE EVENT.
        status_info = get_status_info(self.__test_id, event_type,
                                      event_subtype, event_value,
                                      event_time, event_filename)
        event_record_string = event_time + '\t' + event_value
        status_info_dict = {}
        for key_value in status_info:
            event_record_string += '\t' + key_value[0] + '=' + key_value[1]
            # Remap into an easier to use format
            status_info_dict[key_value[0]] = key_value[1]
        event_record_string += '\n'

        machine_name=""
        if 'LMOD_SYSTEM_NAME' in os.environ:
            machine_name = os.environ['LMOD_SYSTEM_NAME']
        else:
            machine_name = subprocess.run("hostname --fqdn", shell=True, stdout=subprocess.PIPE).stdout.strip()

        influx_event_record_string = "events,job_id=" + str(self.__test_id) + ",app=" + status_info_dict["app"] + ",test=" + status_info_dict["test"] + ",runtag=" + status_info_dict["runtag"] + ",machine="  + machine_name + " "
        for key_value in status_info:
            influx_event_record_string += key_value[0] + '="' + key_value[1] + '",'

        event_time_unix = dateutil.parser.parse(status_info_dict['event_time']).strftime('%s%f') + "000"

        # Add handling for pasting outputs to influxdb

        if status_info_dict['event_name'] == "build_end":
            file_name = status_info_dict['run_archive'] + "/build_directory/" + "output_build.txt"
            print(file_name)
            if os.path.exists(file_name):
                with open(file_name, "r") as f:
                    output = f.read()
                    # Truncate to 64 kb
                    output = output[-65534:].replace('"', '\\"')
                    influx_event_record_string = influx_event_record_string + "output_txt=\"" + output + "\","

        if status_info_dict['event_name'] == "submit_end":
            file_name = status_info_dict['run_archive'] + "/" + "submit.err"
            print(file_name)
            if os.path.exists(file_name):
                with open(file_name, "r") as f:
                    output = f.read()
                    # Truncate to 64 kb
                    output = output[-65534:].replace('"', '\\"')
                    influx_event_record_string = influx_event_record_string + "output_txt=\"" + output + "\","

        if status_info_dict['event_name'] == "binary_execute_end":
            for file_name in glob.glob(status_info_dict['run_archive'] + "/*.o" + status_info_dict['job_id']):
                print(file_name)
                if os.path.exists(file_name):
                    with open(file_name, "r") as f:
                        output = f.read()
                        # Truncate to 64 kb
                        output = output[-65534:].replace('"', '\\"')
                        influx_event_record_string = influx_event_record_string + "output_txt=\"" + output + "\","

        if status_info_dict['event_name'] == "check_end":
            file_name = status_info_dict['run_archive'] + "/" + "output_check.txt"
            print(file_name)
            if os.path.exists(file_name):
                with open(file_name, "r") as f:
                    output = f.read()
                    # Truncate to 64 kb
                    output = output[-65534:].replace('"', '\\"')
                    influx_event_record_string = influx_event_record_string + "output_txt=\"" + output + "\","

        influx_event_record_string = influx_event_record_string.strip(',') + " " + str(event_time_unix)


        # Write a temporary file with the event info, then
        # (atomically) rename it to the permanent file,
        # to avoid possibility of a partially completed file.

        dir_head = os.path.split(os.getcwd())[0]
        file_path = os.path.join(dir_head, apptest_layout.test_status_dirname, str(self.__test_id),
                                 event_filename)
        if os.path.exists(file_path):
            print('Warning: event log file already exists. ' + file_path)

        file_path_partial = os.path.join(dir_head, apptest_layout.test_status_dirname,
                                         str(self.__test_id),
                                         'partial.' + event_filename)

        file_ = open(file_path_partial, 'w')
        file_.write(event_record_string)
        file_.close()

        # THE FOLLOWING CREATES THE OFFICIAL MASTER INDICATOR DENOTING
        # THAT THE EVENT OCCURRED.
        os.rename(file_path_partial, file_path)

        # Put the same event data on the system log.

        write_system_log(self.__test_id, status_info)

        # Write event to InfluxDB
        if 'RGT_INFLUX_URI' in os.environ and 'RGT_INFLUX_TOKEN' in os.environ:
            influx_url = os.environ['RGT_INFLUX_URI']
            influx_token = os.environ['RGT_INFLUX_TOKEN']
            
            print("Logging event to influx")
            print(influx_event_record_string)
            headers = {'Authorization': "Token " + influx_token, 'Content-Type': "text/plain; charset=utf-8", 'Accept': "application/json"}

            try:
                r = requests.post(influx_url, data=influx_event_record_string, headers=headers)
            except:
                print(r.text)

        # Update the status file appropriately.
        if event_id == StatusFile.EVENT_BUILD_END:
            self.__status_file_add_result(event_value, mode="Add_Build_Result")
        elif event_id == StatusFile.EVENT_SUBMIT_START:
            self.__status_file_add_result(event_value, mode="Add_Run_Count")
        elif event_id == StatusFile.EVENT_SUBMIT_END:
            self.__status_file_add_result(event_value, mode="Add_Submit_Result")
        elif event_id == StatusFile.EVENT_JOB_QUEUED:
            self.__status_file_add_result(event_value, mode="Add_Job_ID")
            self.__status_file_add_result('-1', mode="Add_Run_Aborning")
        elif event_id == StatusFile.EVENT_BINARY_EXECUTE_START:
            self.__status_file_add_result(event_value,
                                          mode="Add_Binary_Running")
        elif event_id == StatusFile.EVENT_CHECK_END:
            self.__status_file_add_result(event_value, mode="Add_Run_Result")

        return event_time

    #----------

    def __create_status_file(self,path_to_status_file):
        """Create the status file for this app/test if it doesn't exist."""
        if not os.path.exists(path_to_status_file):
            with open(self.__status_file_path, "w") as file_obj :
                file_obj.write(StatusFile.header)

    #----------

    def __status_file_add_result(self, event_value, mode):
        """Update the status file to reflect a new event."""

        #---Read the status file.
        status_file = open(self.__status_file_path, 'r')
        records = status_file.readlines()
        status_file.close()
        #event_time = datetime.datetime.now().isoformat()

        for index, line in enumerate(records):

            # Get the uid for this run instance

            words = line.rstrip().split()

            if len(words) < len(StatusFile.STATUS_COLUMNS):
                continue

            test_id = words[StatusFile.STATUS_COLUMNS[StatusFile.STATUS_COLUMN_UNIQUE]]

            if test_id != self.__test_id:
                continue

            if mode == 'Add_Job_ID':
                batch_col = StatusFile.STATUS_COLUMNS[StatusFile.STATUS_COLUMN_BATCH]
                words[batch_col] = event_value

            if mode == 'Add_Build_Result':
                build_col = StatusFile.STATUS_COLUMNS[StatusFile.STATUS_COLUMN_BUILD]
                words[build_col] = event_value

            if mode == 'Add_Run_Count':
                count_col = StatusFile.STATUS_COLUMNS[StatusFile.STATUS_COLUMN_COUNT]
                words[count_col] = event_value

            if mode == 'Add_Submit_Result':
                submit_col = StatusFile.STATUS_COLUMNS[StatusFile.STATUS_COLUMN_SUBMIT]
                words[submit_col] = event_value

            if mode == 'Add_Run_Result':
                check_col = StatusFile.STATUS_COLUMNS[StatusFile.STATUS_COLUMN_CHECK]
                words[check_col] = event_value

            if mode == 'Add_Binary_Running':
                binary_running_value = event_value

                check_col = StatusFile.STATUS_COLUMNS[StatusFile.STATUS_COLUMN_CHECK]
                words[check_col] = binary_running_value

                dir_head = os.path.split(os.getcwd())[0]
                path2 = os.path.join(dir_head, apptest_layout.test_status_dirname, test_id,
                                     apptest_layout.job_status_filename)
                file_obj2 = open(path2, 'w')
                file_obj2.write(binary_running_value)
                file_obj2.close()

            if mode == 'Add_Run_Aborning':
                aborning_run_value = event_value
                check_col = StatusFile.STATUS_COLUMNS[StatusFile.STATUS_COLUMN_CHECK]
                words[check_col] = aborning_run_value

                dir_head = os.path.split(os.getcwd())[0]
                path2 = os.path.join(dir_head, apptest_layout.test_status_dirname, test_id,
                                     apptest_layout.job_status_filename)
                file_obj2 = open(path2, 'w')
                file_obj2.write(aborning_run_value)
                file_obj2.close()

            records[index] = StatusFile.__LINE_FORMAT % (
                words[StatusFile.STATUS_COLUMNS[StatusFile.STATUS_COLUMN_START]],
                words[StatusFile.STATUS_COLUMNS[StatusFile.STATUS_COLUMN_LAUNCH]],
                words[StatusFile.STATUS_COLUMNS[StatusFile.STATUS_COLUMN_UNIQUE]],
                words[StatusFile.STATUS_COLUMNS[StatusFile.STATUS_COLUMN_COUNT]],
                words[StatusFile.STATUS_COLUMNS[StatusFile.STATUS_COLUMN_BATCH]],
                words[StatusFile.STATUS_COLUMNS[StatusFile.STATUS_COLUMN_BUILD]],
                words[StatusFile.STATUS_COLUMNS[StatusFile.STATUS_COLUMN_SUBMIT]],
                words[StatusFile.STATUS_COLUMNS[StatusFile.STATUS_COLUMN_CHECK]])

        #---Update the status file.
        status_file = open(self.__status_file_path, 'w')
        status_file.writelines(records)
        status_file.close()

    #----------

    def __status_file_add_test_instance(self, event_time, launch_id, unique_id):
        """Start new line in master status file for app/test."""

        with open(self.__status_file_path, "a") as file_obj:
            format_ = StatusFile.__LINE_FORMAT % (
                event_time, launch_id, unique_id, StatusFile.PLACE_HOLDER,
                StatusFile.PLACE_HOLDER, StatusFile.PLACE_HOLDER,
                StatusFile.PLACE_HOLDER, StatusFile.PLACE_HOLDER)
            file_obj.write(format_)

#------------------------------------------------------------------------------

def get_status_info(test_id, event_type, event_subtype,
                    event_value, event_time, event_filename):
    """Create a data structure with verbose info for an event."""

    no_value = StatusFile.NO_VALUE

    #---Set up dicts to capture info.

    test_instance_info = {}
    event_info = {}

    #---Construct fields to be used for log entry.

    test_instance_info['user'] = os.environ['USER']
    test_instance_info['hostname'] = socket.gethostname()
    test_instance_info['cwd'] = os.getcwd()

    (dir_head1, dir_scripts) = os.path.split(test_instance_info['cwd'])
    assert dir_scripts == apptest_layout.test_scripts_dirname, (
        'harness function being executed from wrong directory.')
    (dir_head2, test_) = os.path.split(dir_head1)
    test_instance_info['test'] = test_
    test_instance_info['app'] = os.path.split(dir_head2)[1]
    test_instance_info['test_id'] = test_id
    test_instance_info['test_instance'] = (
        test_instance_info['app'] + ',' +
        test_instance_info['test'] + ',' +
        test_instance_info['test_id'])

    dir_status = os.path.join(dir_head1, apptest_layout.test_status_dirname)
    dir_status_this_test = os.path.join(dir_status, test_id)

    run_archive_all = os.path.join(dir_head1, apptest_layout.test_run_archive_dirname)
    test_instance_info['run_archive'] = os.path.join(run_archive_all, test_id)

    test_instance_info['rgt_path_to_sspace'] = os.environ['RGT_PATH_TO_SSPACE']

    test_instance_info['build_directory'] = os.path.join(
        test_instance_info['rgt_path_to_sspace'],
        test_instance_info['app'],
        test_instance_info['test'],
        test_instance_info['test_id'], apptest_layout.test_build_dirname)

    test_instance_info['workdir'] = os.path.join(
        test_instance_info['rgt_path_to_sspace'],
        test_instance_info['app'],
        test_instance_info['test'],
        test_instance_info['test_id'], apptest_layout.test_run_dirname)

    job_account = no_value
    if 'RGT_PROJECT_ID' in os.environ:
        job_account = os.environ['RGT_PROJECT_ID']
    elif 'RGT_ACCT_ID' in os.environ:
        job_account = os.environ['RGT_ACCT_ID']
    test_instance_info['job_account_id'] = job_account

    test_instance_info['path_to_rgt_package'] = (
        os.environ['PATH_TO_RGT_PACKAGE']
        if 'PATH_TO_RGT_PACKAGE' in os.environ else no_value)

    test_instance_info['rgt_system_log_tag'] = (
        os.environ['RGT_SYSTEM_LOG_TAG']
        if 'RGT_SYSTEM_LOG_TAG' in os.environ else no_value)

    #---

    event_info['event_name'] = event_type + '_' + event_subtype
    event_info['event_type'] = event_type
    event_info['event_subtype'] = event_subtype
    event_info['event_time'] = event_time
    event_info['event_filename'] = event_filename
    event_info['event_value'] = (
        str(event_value) if event_value is not None else no_value)

    event_info['runtag'] = test_instance_info['rgt_system_log_tag']

    file_job_id = os.path.join(dir_status_this_test, apptest_layout.job_id_filename)
    if os.path.exists(file_job_id):
        file_ = open(file_job_id, 'r')
        job_id_ = file_.read()
        file_.close()
        event_info['job_id'] = re.sub(' ', '', job_id_.split('\n')[0])
    else:
        event_info['job_id'] = no_value

    file_job_status = os.path.join(dir_status_this_test, apptest_layout.job_status_filename)
    if os.path.exists(file_job_status):
        file_ = open(file_job_status, 'r')
        job_status_ = file_.read()
        file_.close()
        event_info['job_status'] = re.sub(' ', '', job_status_.split('\n')[0])
    else:
        event_info['job_status'] = no_value

    #---Construct status_info.

    status_info = []

    #---NOTE: order matters here.  It is assumed (by Splunk) that
    #---all items strictly after test_instance will be invariant
    #---across all events for a given test instance.
    assert StatusFile.FIELDS_PER_TEST_INSTANCE[-1] == 'test_instance'

    for field in StatusFile.FIELDS_PER_TEST_INSTANCE:
        status_info.append([field, test_instance_info[field]])

    for field in StatusFile.FIELDS_PER_EVENT:
        status_info.append([field, event_info[field]])

    for field in StatusFile.FIELDS_SPLUNK_SPECIAL:
        #---Something extra to help Splunk:
        status_info.append([event_info['event_name']+'_'+field,
                            event_info[field]])

    return status_info

#------------------------------------------------------------------------------

def write_system_log(test_id, status_info):
    """Write a system log entry for an event."""

    #---Use Unix logger command unless (valid) directory requested.

    rgt_system_log_dir = (os.environ['RGT_SYSTEM_LOG_DIR']
        if 'RGT_SYSTEM_LOG_DIR' in os.environ else '')

    is_using_unix_logger = False
    if rgt_system_log_dir == '':
        is_using_unix_logger = True
    elif not os.path.exists(rgt_system_log_dir):
        is_using_unix_logger = True

    rgt_system_log_tag = (os.environ['RGT_SYSTEM_LOG_TAG']
        if 'RGT_SYSTEM_LOG_TAG' in os.environ else '')

    if rgt_system_log_tag == '':
        return

    #---Construct log string.

    #TODO: make quote a function ...

    quote = '\\"' if is_using_unix_logger else '"'

    log_string = ''

    for key_value in status_info:
        if log_string != '':
            log_string += ' '
        log_string += key_value[0] + '=' + quote + key_value[1] + quote

    #---Write log.

    if is_using_unix_logger:
        os.system('logger -p local0.notice "' + log_string + '"')

    else:
        dir_head1 = os.path.split(os.getcwd())[0]
        (dir_head2, test) = os.path.split(dir_head1)
        app = os.path.split(dir_head2)[1]

        log_file = (app + '_#_' +
                    test + '_#_' +
                    test_id + #---Alt: could use uuid.uuid1()
                    '.txt')
        log_path = os.path.join(rgt_system_log_dir, log_file)

        file_ = open(log_path, 'a')
        file_.write(log_string + '\n')
        file_.close()

#------------------------------------------------------------------------------

def parse_status_file(path_to_status_file, startdate, enddate,
                      mycomputer_with_events_record):
    """Function: parse_status_file. Parser for rgt_status_file.txt"""

    number_of_tests = 0
    number_of_passed_tests = 0
    number_of_failed_tests = 0
    number_of_inconclusive_tests = 0

    shash = {"number_of_tests": number_of_tests,
             "number_of_passed_tests": number_of_passed_tests,
             "number_of_failed_tests": number_of_failed_tests,
             "number_of_inconclusive_tests": number_of_inconclusive_tests}

    failed_jobs = []

    if os.path.exists(path_to_status_file):
        pass
    else:
        return shash

    sfile_obj = open(path_to_status_file, 'r')
    sfile_lines = sfile_obj.readlines()
    sfile_obj.close()

    start_col  = StatusFile.STATUS_COLUMNS[StatusFile.STATUS_COLUMN_START]
    batch_col  = StatusFile.STATUS_COLUMNS[StatusFile.STATUS_COLUMN_BATCH]
    build_col  = StatusFile.STATUS_COLUMNS[StatusFile.STATUS_COLUMN_BUILD]
    submit_col = StatusFile.STATUS_COLUMNS[StatusFile.STATUS_COLUMN_SUBMIT]
    check_col  = StatusFile.STATUS_COLUMNS[StatusFile.STATUS_COLUMN_CHECK]

    print("parsing status file: " + path_to_status_file)
    for line in sfile_lines:
        tmpline = line.lstrip()
        if not StatusFile.ignore_line(tmpline):
            number_of_tests += 1
            words = tmpline.split()

            #Get the creation time.
            creationtime = words[start_col]

            #Get the job id.
            jobid1 = words[batch_col]
            jobid2 = jobid1.split(".")
            jobid = jobid2[0]

            # Get the number of passed tests.
            #Conservative check
            if (mycomputer_with_events_record.in_time_range(jobid, creationtime, startdate, enddate) and
                words[build_col].isdigit() and words[submit_col].isdigit() and words[check_col].isdigit()):
                check_val = int(words[check_col])
                if check_val == 0:
                    number_of_passed_tests += 1
                elif check_val == 1:
                    number_of_failed_tests += 1
                elif check_val >= 2:
                    number_of_inconclusive_tests += 1
            else:
                number_of_tests -= 1

    shash = {"number_of_tests": number_of_tests,
             "number_of_passed_tests": number_of_passed_tests,
             "number_of_failed_tests": number_of_failed_tests,
             "number_of_inconclusive_tests": number_of_inconclusive_tests}


    return shash, failed_jobs

#------------------------------------------------------------------------------

def parse_status_file2(path_to_status_file):
    """Function: parse_status_file2. Parser for rgt_status_file.txt"""

    number_of_tests = 0
    number_of_passed_tests = 0
    number_of_failed_tests = 0
    number_of_inconclusive_tests = 0

    shash = {'number_of_tests': number_of_tests,
             'number_of_passed_tests': number_of_passed_tests,
             'number_of_failed_tests': number_of_failed_tests,
             'number_of_inconclusive_tests': number_of_inconclusive_tests}

    failed_jobs = []

    if not os.path.exists(path_to_status_file):
        return shash

    sfile_obj = open(path_to_status_file, 'r')
    sfile_lines = sfile_obj.readlines()
    sfile_obj.close()

    build_col  = StatusFile.STATUS_COLUMNS[StatusFile.STATUS_COLUMN_BUILD]
    submit_col = StatusFile.STATUS_COLUMNS[StatusFile.STATUS_COLUMN_SUBMIT]
    check_col  = StatusFile.STATUS_COLUMNS[StatusFile.STATUS_COLUMN_CHECK]

    print('Parsing status file ' + path_to_status_file)
    for line in sfile_lines:
        tmpline = line.lstrip()
        if not StatusFile.ignore_line(tmpline):
            number_of_tests += 1
            words = tmpline.split()

            # Get the number of passed tests.
            # Conservative check
            if words[build_col].isdigit() and words[submit_col].isdigit() and words[check_col].isdigit():
                check_val = int(words[check_col])
                if check_val == 0:
                    number_of_passed_tests += 1
                elif check_val == 1:
                    number_of_failed_tests += 1
                elif check_val >= 2:
                    number_of_inconclusive_tests += 1
            else:
                number_of_tests -= 1

    shash = {'number_of_tests': number_of_tests,
             'number_of_passed_tests': number_of_passed_tests,
             'number_of_failed_tests': number_of_failed_tests,
             'number_of_inconclusive_tests': number_of_inconclusive_tests}

    #print("shash=", shash)
    #print("failed_jobs=", failed_jobs)
    print('Status dict:')
    pprint.pprint(shash)
    print('Failed jobs: ', failed_jobs)
    return shash, failed_jobs

#------------------------------------------------------------------------------

def summarize_status_file(path_to_status_file, startdate, enddate,
                          mycomputer_with_events_record):
    """Parse, collect summary info from rgt_status.txt."""
    sfile_obj = open(path_to_status_file, 'r')
    sfile_lines = sfile_obj.readlines()
    sfile_obj.close()

    number_of_tests = 0
    number_of_passed_tests = 0
    number_of_failed_tests = 0
    number_of_inconclusive_tests = 0

    start_col  = StatusFile.STATUS_COLUMNS[StatusFile.STATUS_COLUMN_START]
    unique_col = StatusFile.STATUS_COLUMNS[StatusFile.STATUS_COLUMN_UNIQUE]
    batch_col  = StatusFile.STATUS_COLUMNS[StatusFile.STATUS_COLUMN_BATCH]
    build_col  = StatusFile.STATUS_COLUMNS[StatusFile.STATUS_COLUMN_BUILD]
    submit_col = StatusFile.STATUS_COLUMNS[StatusFile.STATUS_COLUMN_SUBMIT]
    check_col  = StatusFile.STATUS_COLUMNS[StatusFile.STATUS_COLUMN_CHECK]

    flist = []
    ilist = []
    print("parsing status file: " + path_to_status_file)
    for line in sfile_lines:
        tmpline = line.lstrip()
        if len(tmpline) > 0 and tmpline[0] != StatusFile.COMMENT_LINE_INDICATOR:
            words = tmpline.split()

            #Get the job id.
            jobid1 = words[batch_col]
            jobid2 = jobid1.split(".")
            jobid = jobid2[0]

            print("====")
            print("Test instance: " + tmpline)
            print("job id: " + jobid)

            #Get the creation time.
            creationtime = words[start_col]
            #(creationtime1, creationtime2) = creationtime.split("T")
            creationtime1 = creationtime.split("T")[0]
            (year, month, day) = creationtime1.split("-")
            #(time1, time2) = creationtime2.split(".")
            #(hour, min, sec) = time1.split(":")
            creationdate = datetime.datetime(int(year), int(month), int(day))

            testid = words[unique_col]

            # Get the number of passed tests.
            #Conservative check
            if (mycomputer_with_events_record.in_time_range(jobid, creationtime, startdate, enddate)):
                print("In range")

                number_of_tests += 1

                if (words[build_col].isdigit() and
                    words[submit_col].isdigit() and
                    words[check_col].isdigit()):
                    check_val = int(words[check_col])
                    if check_val == 0:
                        number_of_passed_tests += 1
                    elif check_val >= 1:
                        number_of_failed_tests += 1
                        flist = flist + [testid]
                    elif check_val == -1:
                        number_of_inconclusive_tests += 1
                        ilist = ilist + [testid]

                elif (words[build_col] == StatusFile.PLACE_HOLDER or
                      words[submit_col] == StatusFile.PLACE_HOLDER or
                      words[check_col] == StatusFile.PLACE_HOLDER):
                    number_of_inconclusive_tests += 1

            elif (startdate <= creationdate and
                  creationdate <= enddate and
                  jobid == StatusFile.PLACE_HOLDER):
                print("In range")
                number_of_tests += 1
                number_of_inconclusive_tests += 1
                ilist = ilist + [testid]

            print(f"number of tests = {number_of_tests}")
            print("====")
            print()
            print()

    shash = {"number_of_tests": number_of_tests,
             "number_of_passed_tests": number_of_passed_tests,
             "number_of_failed_tests": number_of_failed_tests,
             "number_of_inconclusive_tests": number_of_inconclusive_tests,
             "failed_jobs": flist,
             "inconclusive_jobs": ilist}

    return shash

#------------------------------------------------------------------------------

#-----------------------------------------------------
#                                                    -
# Start of defining errors classes for this module.  -
#                                                    -
#-----------------------------------------------------

class StatusFileError(Exception):
    """Base class for exceptions of the StatusFile"""
    def __init__(self):
        pass

    @property
    @abc.abstractmethod
    def message(self):
        pass

class IncompatibleStatusFileModeError(StatusFileError):
    """Exception raised for errors of incompatible modes for various StatusFile tasks."""
    def __init__(self,message):
        """The class constructor

        Parameters
        ----------
        message : string
            The error message for this exception.
        """
        self._message = message

    @property
    def message(self):
        """str: The error message."""
        return self._message

class InvalidStatusFileModeError(StatusFileError):
    """Exception raised for error of invalid mode for StatusFile."""
    def __init__(self,message):
        """The class constructor

        Parameters
        ----------
        message : string
            The error message for this exception.
        """
        self._message = message

    @property
    def message(self):
        """str: The error message."""
        return self._message

class StatusFileMissingError(StatusFileError):
    """Exception raised for missing status file."""
    def __init__(self,message):
        """The class constructor

        Parameters
        ----------
        message : string
            The error message for this exception.
        """
        self._message = message

    @property
    def message(self):
        """str: The error message."""
        return self._message

#-----------------------------------------------------
#                                                    -
# End of defining errors classes for this module.    -
#                                                    -
#-----------------------------------------------------
