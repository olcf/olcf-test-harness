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

    line_format = "%-30s %-21s %-20s %-15s %-15s %-15s\n"

    # Header lines for status.
    header1 = line_format % (' ', ' ', ' ', ' ', ' ', ' ')
    header2 = str.replace(header1, ' ', '#')
    header3 = line_format % ('#Start Time', 'Unique ID', 'Batch ID',
                             'Build Status', 'Submit Status', 'Correct Results')
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
    comment_line_entry = '#'

    FAILURE_CODES = {'Pass_Fail': 0,
                     'Hardware_Failure': 1,
                     'Performance_Failure': 2,
                     'Incorrect_Result': 3
                    }

    #################
    # Class methods #
    #################

    @staticmethod
    def ignore_line(a_line):
        """
        """
        result = False

        tmpline = a_line.strip()

        if len(tmpline) > 0:
            if tmpline[0] == StatusFile.comment_line_entry:
                result = True
        else:
            result = True

        return result

    ###################
    # Special methods #
    ###################

    def __init__(self, unique_id, mode):
        """Constructor."""
        self.__job_id = ''
        self.__path_to_file = ''
        self.__unique_id = unique_id

        # Make the status file.
        self.__make_status_file()

        # Add job to status file.
        if mode == 'New':
            self.__add_job()

        elif mode == 'Old':
            pass

    ###################
    # Public methods  #
    ###################

    def add_result(self, exit_value, mode):
        """Update the status file to reflect new event."""

        #---Initial read of status file.
        status_file = open(self.__path_to_file, 'r')
        records1 = status_file.readlines()
        status_file.close()
        event_time = datetime.datetime.now().isoformat()

        for index, line in enumerate(records1):

            # If the first character is a "#" then ignore record.
            #line0 = str.strip(line)
            #if True:
            #    pass

            # Get the uid for this run instance

            line1 = str.rstrip(line)
            words1 = str.split(line1)

            if len(words1) >= 6:
                #stime1 = words1[0]
                uid1 = words1[1]

                #if uid1 != self.__unique_id:
                #    continue

                if uid1 == self.__unique_id:
                    if mode == 'Add_Job_ID':
                        words1[2] = exit_value

                    if mode == 'Add_Build_Result':
                        words1[3] = exit_value
                        self.__write_system_log('build_result',
                                                str(exit_value), event_time)

                    if mode == 'Add_Submit_Result':
                        words1[4] = exit_value
                        self.__write_system_log('submit_result',
                                                str(exit_value), event_time)

                    if mode == 'Add_Run_Result':
                        words1[5] = exit_value
                        self.__write_system_log('run_result',
                                                str(exit_value), event_time)

                    if mode == 'Add_Binary_Running':
                        binary_running_value = exit_value

                        words1[5] = binary_running_value

                        cwd = os.getcwd()
                        #(dir_head1, dir_tail1) = os.path.split(cwd)
                        dir_head1 = os.path.split(cwd)[0]
                        path2 = os.path.join(dir_head1, 'Status', uid1,
                                             'job_status.txt')
                        file_obj2 = open(path2, 'w')
                        file_obj2.write(binary_running_value)
                        file_obj2.close()
                        self.__write_system_log('binary_running',
                                                str(exit_value), event_time)

                    if mode == 'Add_Run_Aborning':
                        abornining_run_value = exit_value

                        words1[5] = abornining_run_value

                        cwd = os.getcwd()
                        #(dir_head1, dir_tail1) = os.path.split(cwd)
                        dir_head1 = os.path.split(cwd)[0]
                        path2 = os.path.join(dir_head1, 'Status', uid1,
                                             'job_status.txt')
                        file_obj2 = open(path2, 'w')
                        file_obj2.write(abornining_run_value)
                        file_obj2.close()
                        self.__write_system_log('run_aborning',
                                                str(exit_value), event_time)

                    records1[index] = StatusFile.line_format % (
                        (words1[0], words1[1], words1[2], words1[3],
                         words1[4], words1[5]))

        #---Update the status file.
        status_file = open(self.__path_to_file, 'w')
        status_file.writelines(records1)
        status_file.close()

    def log_build_start_time(self):
        """Write log message to denote app build has started."""
        currenttime = datetime.datetime.now()

        cwd = os.getcwd()

        # Get the head dir in cwd.
        #(dir_head1, dir_tail1) = os.path.split(cwd)
        dir_head1 = os.path.split(cwd)[0]

        path_to_file = os.path.join(
            dir_head1, 'Status', str(self.__unique_id),
            StatusFile.filename_build_beg_timestamp)
        file_obj = open(path_to_file, 'a')
        file_obj.write(currenttime.isoformat())
        file_obj.close()

        event_time = currenttime.isoformat()
        self.__write_system_log('build', 'start', event_time)

    def log_build_end_time(self):
        """Write log message to denote app build has ended."""
        currenttime = datetime.datetime.now()

        cwd = os.getcwd()

        # Get the head dir in cwd.
        #(dir_head1, dir_tail1) = os.path.split(cwd)
        dir_head1 = os.path.split(cwd)[0]

        path_to_file = os.path.join(
            dir_head1, 'Status', str(self.__unique_id),
            StatusFile.filename_build_end_timestamp)
        file_obj = open(path_to_file, 'a')
        file_obj.write(currenttime.isoformat())
        file_obj.close()

        event_time = currenttime.isoformat()
        self.__write_system_log('build', 'end', event_time)

    def log_submit_start_time(self):
        """Write log message to denote job submission has started."""
        currenttime = datetime.datetime.now()

        cwd = os.getcwd()

        # Get the head dir in cwd.
        #(dir_head1, dir_tail1) = os.path.split(cwd)
        dir_head1 = os.path.split(cwd)[0]

        path_to_file = os.path.join(
            dir_head1, 'Status', str(self.__unique_id),
            StatusFile.filename_submit_beg_timestamp)
        file_obj = open(path_to_file, 'a')
        file_obj.write(currenttime.isoformat())
        file_obj.close()

        event_time = currenttime.isoformat()
        self.__write_system_log('submit', 'start', event_time)

    def log_submit_end_time(self):
        """Write log message to denote job submission has ended."""
        currenttime = datetime.datetime.now()

        cwd = os.getcwd()

        # Get the head dir in cwd.
        #(dir_head1, dir_tail1) = os.path.split(cwd)
        dir_head1 = os.path.split(cwd)[0]

        path_to_file = os.path.join(
            dir_head1, "Status", str(self.__unique_id),
            StatusFile.filename_submit_end_timestamp)
        file_obj = open(path_to_file, "a")
        file_obj.write(currenttime.isoformat())
        file_obj.close()

        event_time = currenttime.isoformat()
        self.__write_system_log('submit', 'end', event_time)

    def log_start_execution_time(self):
        """Write log message to denote execution of app binary has started."""
        currenttime = datetime.datetime.now()

        cwd = os.getcwd()

        # Get the head dir in cwd.
        #(dir_head1, dir_tail1) = os.path.split(cwd)
        dir_head1 = os.path.split(cwd)[0]

        path_to_file = os.path.join(
            dir_head1, 'Status', str(self.__unique_id),
            StatusFile.filename_exec_beg_timestamp)
        file_obj = open(path_to_file, 'a')
        file_obj.write(currenttime.isoformat())
        file_obj.close()

        event_time = currenttime.isoformat()
        self.__write_system_log('binary_execute', 'start', event_time)

    def log_final_execution_time(self):
        """Write log message to denote execution of app binary has ended."""
        currenttime = datetime.datetime.now()

        cwd = os.getcwd()

        # Get the head dir in cwd.
        #(dir_head1, dir_tail1) = os.path.split(cwd)
        dir_head1 = os.path.split(cwd)[0]

        path_to_file = os.path.join(
            dir_head1, 'Status', str(self.__unique_id),
            StatusFile.filename_exec_end_timestamp)

        file_obj = open(path_to_file, 'a')
        file_obj.write(currenttime.isoformat())
        file_obj.close()

        event_time = currenttime.isoformat()
        self.__write_system_log('binary_execute', 'end', event_time)

    ###################
    # Private methods #
    ###################

    def __make_status_file(self):
        """Create the master status file for this app/test if doesn't exist."""

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

    def __add_job(self):
        """Start new line in master status file for app/test."""
        currenttime = datetime.datetime.now()
        file_obj = open(self.__path_to_file, "a")
        format_ = StatusFile.line_format % (
            (currenttime.isoformat(), self.__unique_id,
             "***", "***", "***", "***"))
        file_obj.write(format_)
        file_obj.close()

    def __write_system_log(self, event_name, event_value, event_time):
        """Write a system log entry for an event."""
        write_system_log(self.__unique_id, event_name, event_value, event_time)

#------------------------------------------------------------------------------

def write_system_log(test_id_string, event_name, event_value, event_time):
    """Write a system log entry for an event."""

    #---Get tag from environment, if set by user.

    rgt_system_log_tag = os.environ['RGT_SYSTEM_LOG_TAG'] \
        if 'RGT_SYSTEM_LOG_TAG' in os.environ else ''

    if rgt_system_log_tag == '':
        return

    #---Use Unix logger command unless (valid) directory requested.

    is_using_unix_logger = False

    rgt_system_log_dir = os.environ['RGT_SYSTEM_LOG_DIR'] \
        if 'RGT_SYSTEM_LOG_DIR' in os.environ else ''

    if rgt_system_log_dir == '':
        is_using_unix_logger = True
    elif not os.path.exists(rgt_system_log_dir):
        is_using_unix_logger = True

    #---Construct fields to be used for log entry.

    user = os.environ['USER']

    cwd = os.getcwd()
    (dir_head1, dir_scripts) = os.path.split(cwd)
    assert dir_scripts == 'Scripts', (
        'write_syatem_log function being executed from wrong directory.')
    (dir_head2, test) = os.path.split(dir_head1)
    #(dir_head3, application) = os.path.split(dir_head2)
    application = os.path.split(dir_head2)[1]

    dir_status = os.path.join(dir_head1, 'Status')
    dir_status_this_test = os.path.join(dir_status, test_id_string)

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
    dir_run_archive_this_test = os.path.join(dir_run_archive, test_id_string)

    rgt_path_to_sspace = os.environ['RGT_PATH_TO_SSPACE']

    build_directory = os.path.join(rgt_path_to_sspace, application, test,
                                   test_id_string, 'build_directory')

    workdir = os.path.join(rgt_path_to_sspace, application, test,
                           test_id_string, 'workdir')

    rgt_pbs_job_accnt_id = os.environ['RGT_PBS_JOB_ACCNT_ID']

    path_to_rgt_package = os.environ['PATH_TO_RGT_PACKAGE']

    #---Construct log string.

    quote = '\\"' if is_using_unix_logger else '"'

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
        'test_id_string=' + quote + test_id_string + quote + ' ' +
        'job_id=' + quote + job_id + quote + ' ' +
        'job_status=' + quote + job_status + quote + ' ' +
        'event_time=' + quote + event_time + quote + ' ' +
        event_name + '_event_value=' + quote + event_value + quote + ' '
        '')
#       'event_name=' + quote + event_name + quote + ' ' +
#       'event_value=' + quote + event_value + quote + ' ' +

    #---Write log.

    if is_using_unix_logger:

        os.system('logger -p local0.notice "' + log_string + '"')

    else:

        log_file = (application + '_#_' +
                    test + '_#_' +
                    test_id_string + #---Alt: could use uuid.uuid1()
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
        if len(tmpline) > 0 and tmpline[0] != StatusFile.comment_line_entry:
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
