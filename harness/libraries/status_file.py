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

from libraries.layout_of_apps_directory import apptest_layout

class StatusFile:
    """Perform operations pertaining to logging the status of jobs."""

    ###################
    # Class variables #
    ###################

    __LINE_FORMAT = "%-30s %-21s %-20s %-15s %-15s %-15s\n"

    #---TODO: upcase/underscore these as needed.

    # Header lines for status.
    header1 = __LINE_FORMAT % (' ', ' ', ' ', ' ', ' ', ' ')
    header2 = str.replace(header1, ' ', '#')
    header3 = __LINE_FORMAT % ('#Start Time', 'Unique ID', 'Batch ID',
                               'Build Status', 'Submit Status',
                               'Correct Results')
    header = header2
    header += header1
    header += header3
    header += header1
    header += header2

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
    CORRECT_RESULTS = {"Pending" : PENDING,
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

    def initialize_subtest(self,unique_id):
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
            self.__status_file_add_test_instance(event_time,unique_id)
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
        if len(words) > 2:
            subtest_harness_id = words[1]
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
      
            # If words[2], words[3], words[4], or words[5] equals StatusFile.PLACE_HOLDER
            # then we are not finished. The test is still in progress.
            words = record.split()
            tmp_words = words[2:] 
            if tmp_words.count(self.PLACE_HOLDER) > 1:
                test_finished = False
            # The last word must indicate that the test is no longer pending and not in progress. 
            elif (int(words[5]) > int(self.CORRECT_RESULTS["Pending"])) and (int(words[5]) != int(self.CORRECT_RESULTS["In progress"])) :
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
            means all tests have 0's for build, sumbit, and correct results. Otherwise a 
            False value is returned.
        """
        ret_value = True

        with open(self.__status_file_path, 'r') as status_file_obj:
            records = status_file_obj.readlines()
        
        verify_test_passed = lambda a_list : True if a_list.count(self.PASS) == 3 else False 

        for index, line in enumerate(records):
            if self.ignore_line(line):
                continue

            words = line.rstrip().split()

            tmp_words = words[2:] 

            ret_value = ret_value and verify_test_passed(tmp_words)
                
        return ret_value

    ###################
    # Private methods #
    ###################
    def _subtest_already_initialized(self,unique_id):
        found_instance = False

        with open(self.__status_file_path, 'r') as status_file_obj:
            records = status_file_obj.readlines()

        for index, line in enumerate(records):
            words = line.rstrip().split()

            if self.ignore_line(line):
                continue

            if len(words) > 1:
                test_id = words[1]
                if test_id == unique_id:
                    found_instance = True
                    break

        return found_instance

    def __get_harness_id_record(self,harness_id):
        record = None
        with open(self.__status_file_path, 'r') as status_file_obj:
            records = status_file_obj.readlines()

        for index, line in enumerate(records):
            if self.ignore_line(line):
                continue
            words = line.rstrip().split()
            if len(words) > 1:
                test_id = words[1]
                if test_id == harness_id:
                    record = line
                    break
        return record

    def __get_all_harness_id(self):
        with open(self.__status_file_path, 'r') as status_file_obj:
            records = status_file_obj.readlines()
        
        harness_ids = []
        for index, line in enumerate(records):
            if self.ignore_line(line):
                continue
            words = line.rstrip().split()
            if len(words) > 1:
                harness_ids.append(words[1])

        return harness_ids

    def __log_event(self, event_id, event_filename, event_type, event_subtype,
                    event_value):
        """Official function to log the occurrence of a harness event.
        """

        # THE FOLLOWING LINE IS THE OFFICIAL TIMESTAMP FOR THE EVENT.
        event_time = datetime.datetime.now().isoformat()

        # THE FOLLOWING FORMS THE OFFICIAL TEXT DESCRIBING THE EVENT.
        status_info = get_status_info(self.__test_id, event_type,
                                      event_subtype, event_value,
                                      event_time, event_filename)
        event_record_string = event_time + '\t' + event_value
        for key_value in status_info:
            event_record_string += '\t' + key_value[0] + '=' + key_value[1]
        event_record_string += '\n'

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

        # Update the status file appropriately.
        if event_id == StatusFile.EVENT_BUILD_END:
            self.__status_file_add_result(event_value, mode="Add_Build_Result")
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

    def __status_file_add_result(self, exit_value, mode):
        """Update the status file to reflect a new event."""

        #---Read the status file.
        status_file = open(self.__status_file_path, 'r')
        records = status_file.readlines()
        status_file.close()
        #event_time = datetime.datetime.now().isoformat()

        for index, line in enumerate(records):

            # Get the uid for this run instance

            words = line.rstrip().split()

            if len(words) < 6:
                continue

            test_id = words[1]

            if test_id != self.__test_id:
                continue

            if mode == 'Add_Job_ID':
                words[2] = exit_value

            if mode == 'Add_Build_Result':
                words[3] = exit_value

            if mode == 'Add_Submit_Result':
                words[4] = exit_value

            if mode == 'Add_Run_Result':
                words[5] = exit_value

            if mode == 'Add_Binary_Running':
                binary_running_value = exit_value

                words[5] = binary_running_value

                dir_head = os.path.split(os.getcwd())[0]
                path2 = os.path.join(dir_head, apptest_layout.test_status_dirname, test_id,
                                     apptest_layout.job_status_filename)
                file_obj2 = open(path2, 'w')
                file_obj2.write(binary_running_value)
                file_obj2.close()

            if mode == 'Add_Run_Aborning':
                aborning_run_value = exit_value
                words[5] = aborning_run_value

                dir_head = os.path.split(os.getcwd())[0]
                path2 = os.path.join(dir_head, apptest_layout.test_status_dirname, test_id,
                                     apptest_layout.job_status_filename)
                file_obj2 = open(path2, 'w')
                file_obj2.write(aborning_run_value)
                file_obj2.close()

            records[index] = StatusFile.__LINE_FORMAT % (
                (words[0], words[1], words[2], words[3], words[4], words[5]))

        #---Update the status file.
        status_file = open(self.__status_file_path, 'w')
        status_file.writelines(records)
        status_file.close()

    #----------

    def __status_file_add_test_instance(self, event_time,unique_id):
        """Start new line in master status file for app/test."""

        with open(self.__status_file_path, "a") as file_obj:
            format_ = StatusFile.__LINE_FORMAT % (
                (event_time, unique_id, "***", "***", "***", "***"))
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

    print("parsing status file: " + path_to_status_file)
    for line in sfile_lines:
        tmpline = line.lstrip()
        if  not StatusFile.ignore_line(tmpline):
            number_of_tests = number_of_tests + 1
            words = tmpline.split()

            #Get the pbs id.
            pbsid1 = words[2]
            pbsid2 = pbsid1.split(".")
            pbsid = pbsid2[0]

            #Get the creation time.
            creationtime = words[0]

            # Get the number of passed tests.
            #Conservative check
            if (mycomputer_with_events_record.
                    in_time_range(pbsid, creationtime, startdate, enddate) and
                    words[3].isdigit() and words[4].isdigit() and
                    words[5].isdigit()):
                if int(words[5]) == 0:
                    number_of_passed_tests = number_of_passed_tests + 1

                if int(words[5]) == 1:
                    number_of_failed_tests = number_of_failed_tests + 1

                if int(words[5]) >= 2:
                    number_of_inconclusive_tests = (
                        number_of_inconclusive_tests + 1)
            else:
                number_of_tests = number_of_tests - 1

            #Agressive check
            #if (words[2].find('.nid') >= 0):
            #    if words[5].isdigit():
            #        if int(words[5]) == 0:
            #            number_of_passed_tests = number_of_passed_tests + 1

            #    if words[5].isdigit():
            #        if (int(words[5])==1 or words[3].find('***') >= 0 or
            #          words[4].find('***') >= 0 or words[5].find('***') >= 0):
            #            number_of_failed_tests = number_of_failed_tests + 1
            #    elif words[5].find('***') >= 0:
            #        if (words[3].find('***') >= 0 or
            #    words[4].find('***') >= 0 or words[5].find('***') >= 0):
            #            number_of_failed_tests = number_of_failed_tests + 1
            #else:
            #    number_of_tests = number_of_tests - 1


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

    print('Parsing status file ' + path_to_status_file)
    for line in sfile_lines:
        tmpline = line.lstrip()
        if not StatusFile.ignore_line(tmpline):
            number_of_tests = number_of_tests + 1
            words = tmpline.split()

            # Get the number of passed tests.
            # Conservative check
            if words[3].isdigit() and words[4].isdigit() and words[5].isdigit():
                if int(words[5]) == 0:
                    number_of_passed_tests = number_of_passed_tests + 1

                if int(words[5]) == 1:
                    number_of_failed_tests = number_of_failed_tests + 1

                if int(words[5]) >= 2:
                    number_of_inconclusive_tests = (
                        number_of_inconclusive_tests + 1)
            else:
                number_of_tests = number_of_tests - 1

            #Agressive check
            #if (words[2].find('.nid') >= 0):
            #    if words[5].isdigit():
            #        if int(words[5]) == 0:
            #            number_of_passed_tests = number_of_passed_tests + 1
            #    if words[5].isdigit():
            #        if (int(words[5])==1 or (words[3].find('***') >= 0) or
            #     (words[4].find('***') >= 0) or ( words[5].find('***') >= 0)):
            #            number_of_failed_tests = number_of_failed_tests + 1
            #    elif words[5].find('***') >= 0:
            #        if ((words[3].find('***') >= 0) or
            #  (words[4].find('***') >= 0) or ( words[5].find('***') >= 0)):
            #            number_of_failed_tests = number_of_failed_tests + 1
            #else:
            #    number_of_tests = number_of_tests - 1


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

    flist = []
    ilist = []
    print("parsing status file: " + path_to_status_file)
    for line in sfile_lines:
        tmpline = line.lstrip()
        if len(tmpline) > 0 and tmpline[0] != StatusFile.COMMENT_LINE_INDICATOR:
            words = tmpline.split()

            #Get the pbs id.
            pbsid1 = words[2]
            pbsid2 = pbsid1.split(".")
            pbsid = pbsid2[0]

            print("====")
            print("Test instance: " + tmpline)
            print("pbs job id: " + pbsid)

            #Get the creation time.
            creationtime = words[0]
            #(creationtime1, creationtime2) = creationtime.split("T")
            creationtime1 = creationtime.split("T")[0]
            (year, month, day) = creationtime1.split("-")
            #(time1, time2) = creationtime2.split(".")
            #(hour, min, sec) = time1.split(":")
            creationdate = datetime.datetime(int(year), int(month), int(day))

            # Get the number of passed tests.
            #Conservative check
            if (mycomputer_with_events_record.
                    in_time_range(pbsid, creationtime, startdate, enddate)):
                print("In range")

                number_of_tests = number_of_tests + 1

                if (words[2].isdigit() and words[3].isdigit() and
                        words[4].isdigit() and words[5].isdigit()):
                    if int(words[5]) == 0:
                        number_of_passed_tests = number_of_passed_tests + 1

                    if int(words[5]) >= 1:
                        number_of_failed_tests = number_of_failed_tests + 1
                        flist = flist + [words[1]]

                    if int(words[5]) == -1:
                        number_of_inconclusive_tests = (
                            number_of_inconclusive_tests + 1)
                        ilist = ilist + [words[1]]

                elif (words[3] == "***" or words[4] == "***" or
                      words[5] == "***"):
                    number_of_inconclusive_tests = (
                        number_of_inconclusive_tests + 1)

            elif (startdate <= creationdate and creationdate <= enddate and
                  pbsid == "***"):
                print("In range")
                number_of_tests = number_of_tests + 1
                number_of_inconclusive_tests = number_of_inconclusive_tests + 1
                ilist = ilist + [words[1]]

            print("number of  tests = " + number_of_tests)
            print("====")
            print()
            print()

            #Agressive check
            #if (words[2].find('.nid') >= 0):
            #    if words[5].isdigit():
            #        if int(words[5]) == 0:
            #            number_of_passed_tests = number_of_passed_tests + 1
            #    if words[5].isdigit():
            #        if ((int(words[5])==1) or (words[3].find('***') >= 0) or
            #  (words[4].find('***') >= 0) or ( words[5].find('***') >= 0)):
            #            number_of_failed_tests = number_of_failed_tests + 1
            #    elif words[5].find('***') >= 0:
            #        if ((words[3].find('***') >= 0) or
            #      (words[4].find('***') >= 0) or ( words[5].find('***') >= 0)):
            #            number_of_failed_tests = number_of_failed_tests + 1
            #else:
            #    number_of_tests = number_of_tests - 1

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
