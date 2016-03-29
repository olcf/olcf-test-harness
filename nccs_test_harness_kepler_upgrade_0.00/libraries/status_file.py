#! /usr/bin/env python
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

#from libraries import computers_1

class StatusFile:
    """Class: parse_status_file."""

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
    FILENAME = 'rgt_status.txt'

    # The timestamp log file names.
    filename_exec_beg_timestamp = 'start_binary_execution_timestamp.txt'
    filename_exec_end_timestamp = 'final_binary_execution_timestamp.txt'

    filename_build_beg_timestamp = 'start_build_execution_timestamp.txt'
    filename_build_end_timestamp = 'final_build_execution_timestamp.txt'

    filename_submit_beg_timestamp = 'start_submit_execution_timestamp.txt'
    filename_submit_end_timestamp = 'final_submit_execution_timestamp.txt'

    # These are the entries in the input file.
    COMMENT_LINE_INDICATOR = '#'

    #FAILURE_CODES = {'Pass_Fail': 0,
    #                 'Hardware_Failure': 1,
    #                 'Performance_Failure': 2,
    #                 'Incorrect_Result': 3
    #                }

    #---Event names.

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

    ###################
    # Special methods #
    ###################

    def __init__(self, test_id, mode):
        """Constructor."""
        self.__job_id = ''
        self.__path_to_file = ''
        self.__test_id = test_id

        # Make the status file.
        self.__make_status_file()

        # Add job to status file.
        if mode == 'New':
            event_time = self.log_event(StatusFile.EVENT_LOGGING_START)
            #currenttime = datetime.datetime.now()
            self.__add_test_instance(event_time)

        elif mode == 'Old':
            pass

    ###################
    # Public methods  #
    ###################

    def add_result(self, exit_value, mode):
        """Update the status file to reflect a new event."""

        #---Read the status file.
        status_file = open(self.__path_to_file, 'r')
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
                #self.__write_system_log('build_result',
                #                        str(exit_value), event_time)

            if mode == 'Add_Submit_Result':
                words[4] = exit_value
                #self.__write_system_log('submit_result',
                #                        str(exit_value), event_time)

            if mode == 'Add_Run_Result':
                words[5] = exit_value
                #self.__write_system_log('run_result',
                #                        str(exit_value), event_time)

            if mode == 'Add_Binary_Running':
                binary_running_value = exit_value

                words[5] = binary_running_value

                dir_head = os.path.split(os.getcwd())[0]
                path2 = os.path.join(dir_head, 'Status', test_id, 'job_status.txt')
                file_obj2 = open(path2, 'w')
                file_obj2.write(binary_running_value)
                file_obj2.close()
                #self.__write_system_log('binary_running',
                #                        str(exit_value), event_time)

            if mode == 'Add_Run_Aborning':
                aborning_run_value = exit_value
                words[5] = aborning_run_value

                dir_head = os.path.split(os.getcwd())[0]
                path2 = os.path.join(dir_head, 'Status', test_id, 'job_status.txt')
                file_obj2 = open(path2, 'w')
                file_obj2.write(aborning_run_value)
                file_obj2.close()
                #self.__write_system_log('run_aborning',
                #                        str(exit_value), event_time)

            records[index] = StatusFile.__LINE_FORMAT % (
                (words[0], words[1], words[2], words[3], words[4], words[5]))

        #---Update the status file.
        status_file = open(self.__path_to_file, 'w')
        status_file.writelines(records)
        status_file.close()

    def log_event(self, event, event_status=None):
        """Official entrypoint to log a harness execution event."""
        #---THE OFFICIAL TIMESTAMP FOR THE EVENT.
        event_time = datetime.datetime.now().isoformat()

        if event in StatusFile.EVENT_DICT:
            event_file_name = StatusFile.EVENT_DICT[event][0]
            event_name = StatusFile.EVENT_DICT[event][1]
            event_value = StatusFile.EVENT_DICT[event][2]
        else:
            print('Warning: event not recognized. ' + event)
            #TODO: figure out how to treat warnings, assertions, etc.

        dir_head = os.path.split(os.getcwd())[0]
        file_path = os.path.join(dir_head, 'Status', str(self.__test_id),
                                 event_file_name)

        if os.path.exists(file_path):
            print('Warning: event log file already exists. ' + file_path)
        #---THE OFFICIAL RECORD OF THE OCCURRENCE OF AN EVENT.
        file_obj = open(file_path, 'w')
        file_obj.write(event_time + '\t')
        file_obj.write((str(event_status) if event_status is not None else '') +
                       '\n')
        file_obj.close()

        self.__write_system_log(event_name, event_value, event_status,
                                event_time)

        #elif event == StatusFile.EVENT_BUILD_START:
        #    pass
        if event == StatusFile.EVENT_BUILD_END:
            self.add_result(event_status, mode="Add_Build_Result")
        #elif event == StatusFile.EVENT_SUBMIT_START:
        #    pass
        elif event == StatusFile.EVENT_SUBMIT_END:
            self.add_result(event_status, mode="Add_Submit_Result")
        elif event == StatusFile.EVENT_JOB_QUEUED:
            self.add_result(event_status, mode="Add_Job_ID")
            self.add_result('-1', mode="Add_Run_Aborning")
        elif event == StatusFile.EVENT_BINARY_EXECUTE_START:
            self.add_result(event_status, mode="Add_Binary_Running")
        #elif event == StatusFile.EVENT_BINARY_EXECUTE_END:
        #    pass
        #elif event == StatusFile.EVENT_CHECK_START:
        #    pass
        elif event == StatusFile.EVENT_CHECK_END:
            self.add_result(event_status, mode="Add_Run_Result")

        return event_time

#TODO: put symlinks in status dir (here or elsewhere)

    ###################
    # Private methods #
    ###################

    def __make_status_file(self):
        """Create the status file for this app/test if doesn't exist."""

        # Get the head dir in cwd.
        cwd = os.getcwd()
        dir_head1 = os.path.split(cwd)[0]

        # Form path to rgt status file.
        self.__path_to_file = os.path.join(dir_head1, "Status",
                                           StatusFile.FILENAME)

        # Create.
        if not os.path.lexists(self.__path_to_file):
            file_obj = open(self.__path_to_file, "w")
            file_obj.write(StatusFile.header)
            file_obj.close()

    def __add_test_instance(self, event_time):
        """Start new line in master status file for app/test."""
        file_obj = open(self.__path_to_file, "a")
        format_ = StatusFile.__LINE_FORMAT % (
            (event_time, self.__test_id, "***", "***", "***", "***"))
        file_obj.write(format_)
        file_obj.close()

    def __write_system_log(self, event_name, event_value, event_status,
                           event_time):
        """Write a system log entry for an event."""
        write_system_log(self.__test_id, event_name, event_value,
                         event_status, event_time)

#------------------------------------------------------------------------------

def write_system_log(test_id, event_name, event_value,
                     event_status, event_time):
    """Write a system log entry for an event."""

    #---Get tag from environment, if set by user.

    rgt_system_log_tag = os.environ['RGT_SYSTEM_LOG_TAG'] \
        if 'RGT_SYSTEM_LOG_TAG' in os.environ else ''

    if rgt_system_log_tag == '':
        return

    #---Use Unix logger command unless (valid) directory requested.

    rgt_system_log_dir = os.environ['RGT_SYSTEM_LOG_DIR'] \
        if 'RGT_SYSTEM_LOG_DIR' in os.environ else ''

    is_using_unix_logger = False
    if rgt_system_log_dir == '':
        is_using_unix_logger = True
    elif not os.path.exists(rgt_system_log_dir):
        is_using_unix_logger = True

    #---Construct fields to be used for log entry.

    user = os.environ['USER']

    cwd = os.getcwd()
    (dir_head1, dir_scripts) = os.path.split(cwd)
    assert dir_scripts == 'Scripts', (
        'write_system_log function being executed from wrong directory.')
    (dir_head2, test) = os.path.split(dir_head1)
    application = os.path.split(dir_head2)[1]

    dir_status = os.path.join(dir_head1, 'Status')
    dir_status_this_test = os.path.join(dir_status, test_id)

    file_job_id = os.path.join(dir_status_this_test, 'job_id.txt')
    if os.path.exists(file_job_id):
        file_ = open(file_job_id, 'r')
        job_id = file_.read()
        file_.close()
        job_id = re.sub(' ', '', job_id.split('\n')[0])
    else:
        job_id = ''

    file_job_status = os.path.join(dir_status_this_test, 'job_status.txt')
    if os.path.exists(file_job_status):
        file_ = open(file_job_status, 'r')
        job_status = file_.read()
        file_.close()
        job_status = re.sub(' ', '', job_status.split('\n')[0])
    else:
        job_status = ''

    dir_run_archive = os.path.join(dir_head1, 'Run_Archive')
    dir_run_archive_this_test = os.path.join(dir_run_archive, test_id)

    rgt_path_to_sspace = os.environ['RGT_PATH_TO_SSPACE']

    build_directory = os.path.join(rgt_path_to_sspace, application, test,
                                   test_id, 'build_directory')

    workdir = os.path.join(rgt_path_to_sspace, application, test,
                           test_id, 'workdir')

    rgt_pbs_job_accnt_id = os.environ['RGT_PBS_JOB_ACCNT_ID']

    path_to_rgt_package = os.environ['PATH_TO_RGT_PACKAGE']

    #---Construct log string.

    #TODO: make quote a function ...

    quote = '\\"' if is_using_unix_logger else '"'

    event_status_string = ('event_status=' + quote +
                           str(event_status) + quote + ' '
                           if event_status is not None else '')

    log_string = (
        'rgt_system_log_tag=' + quote + rgt_system_log_tag + quote + ' ' +
        'user=' + quote + user + quote + ' ' +
        'rgt_pbs_job_accnt_id=' + quote + rgt_pbs_job_accnt_id + quote + ' ' +
        'rgt_path_to_sspace=' + quote + rgt_path_to_sspace + quote + ' ' +
        'path_to_rgt_package=' + quote + path_to_rgt_package + quote + ' ' +
        'build_directory=' + quote + build_directory + quote + ' ' +
        'workdir=' + quote + workdir + quote + ' ' +
        'run_archive=' + quote + dir_run_archive_this_test + quote + ' ' +
        'wd=' + quote + cwd + quote + ' ' +
        'application=' + quote + application + quote + ' ' +
        'test=' + quote + test + quote + ' ' +
        'test_id_string=' + quote + test_id + quote + ' ' +
        'job_id=' + quote + job_id + quote + ' ' +
        'job_status=' + quote + job_status + quote + ' ' +
        'event_time=' + quote + event_time + quote + ' ' +
        event_name + '_event_value=' + quote + event_value + quote + ' ' +
        event_status_string +
        '')

    #---Write log.

    if is_using_unix_logger:
        os.system('logger -p local0.notice "' + log_string + '"')

    else:
        log_file = (application + '_#_' +
                    test + '_#_' +
                    test_id + #---Alt: could use uuid.uuid1()
                    '.txt')
        log_path = os.path.join(rgt_system_log_dir, log_file)

        file_ = open(log_path, 'a')
        file_.write(log_string + '\n')
        file_.close()

#------------------------------------------------------------------------------

class JobExitStatus:
    """
    """

    def __init__(self):
        """Constructor."""
        self.status = {"Pass_Fail": 0,
                       "Hardware_Failure": 0,
                       "Performance_Failure": 0,
                       "Incorrect_Result": 0}

    def change_job_exit_status(self, category="Pass_Fail",
                               new_status="FAILURE"):
        """Change the exit status for a specific failure."""

        if category == "Pass_Fail":
            self.add_pass_fail(pf_failure=new_status)
        elif category == "Hardware_Failure":
            self.add_hardware_failure(hw_failure=new_status)
        elif category == "Performance_Failure":
            self.add_performance_failure(pf_failure=new_status)
        elif category == "Incorrect_Result":
            self.add_incorrect_result_failure(ir_failure=new_status)
        else:
            print("Warning! The category " + category + " is not defined.")
            print("The failure will be categorized a general Pass_Fail.")
            self.add_pass_fail(pf_failure=new_status)

    def add_pass_fail(self, pf_failure="NO_FAILURE"):
        """
        """
        if pf_failure == "FAILURE":
            self.status["Pass_Fail"] = 1
        elif pf_failure == "NO_FAILURE":
            self.status["Pass_Fail"] = 0

    def add_hardware_failure(self, hw_failure="NO_FAILURE"):
        """
        """
        if hw_failure == "FAILURE":
            self.status["Hardware_Failure"] = 1
        elif hw_failure == "NO_FAILURE":
            self.status["Hardware_Failure"] = 0

    def add_performance_failure(self, pf_failure="NO_FAILURE"):
        """
        """
        if pf_failure == "FAILURE":
            self.status["Performance_Failure"] = 1
        elif pf_failure == "NO_FAILURE":
            self.status["Performance_Failure"] = 0

    def add_incorrect_result_failure(self, ir_failure="NO_FAILURE"):
        """
        """
        if ir_failure == "FAILURE":
            self.status["Incorrect_Result"] = 1
        elif ir_failure == "NO_FAILURE":
            self.status["Incorrect_Result"] = 0

#------------------------------------------------------------------------------

def convert_to_job_status(job_exit_status):
    """Convert job status to numerical value. """

    tmpsum = 0

    ival = job_exit_status.status["Pass_Fail"]
    tmpsum = tmpsum + ival*1

    ival = job_exit_status.status["Hardware_Failure"]
    tmpsum = tmpsum + ival*2

    ival = job_exit_status.status["Performance_Failure"]
    tmpsum = tmpsum + ival*4

    ival = job_exit_status.status["Incorrect_Result"]
    tmpsum = tmpsum + ival*8

    return tmpsum

#------------------------------------------------------------------------------

def parse_status_file(path_to_status_file, startdate, enddate,
                      mycomputer_with_events_record):
    """Function: parse_status_file."""

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
    """Function: parse_status_file. """

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
        if not StatusFile.ignore_line(tmpline):
            number_of_tests = number_of_tests + 1
            words = tmpline.split()

            # Get the number of passed tests.
            #Conservative check
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


    shash = {"number_of_tests": number_of_tests,
             "number_of_passed_tests": number_of_passed_tests,
             "number_of_failed_tests": number_of_failed_tests,
             "number_of_inconclusive_tests": number_of_inconclusive_tests}

    print("shash=" + shash)
    print("failed_jobs=" + failed_jobs)
    return shash, failed_jobs

#------------------------------------------------------------------------------

def summarize_status_file(path_to_status_file, startdate, enddate,
                          mycomputer_with_events_record):
    """
    """
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
