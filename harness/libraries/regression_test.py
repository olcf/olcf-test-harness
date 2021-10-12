#! /usr/bin/env python3

# Python imports

import collections
import concurrent.futures
import os
import time

# Harness package imports.
from libraries import apptest
from libraries.subtest_factory import SubtestFactory
from fundamental_types.rgt_state import RgtState
from libraries.rgt_loggers import rgt_logger_factory
from machine_types.machine_factory import MachineFactory

#
# Author: Arnold Tharrington (arnoldt@ornl.gov)
# National Center for Computational Sciences, Scientific Computing Group.
# Oak Ridge National Laboratory
#

class Harness:

    # These strings define the tasks that the tests can do.
    checkout = "check_out_tests"
    starttest = "start_tests"
    stoptest = "stop_tests"
    displaystatus = "display_status"
    summarize_results = "summarize_results"

    # Defines the harness log file name.
    LOGGER_NAME = __name__

    #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
    #                                                                 @
    # Special methods                                                 @
    #                                                                 @
    #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

    def __init__(self,
                 config,
                 rgt_input_file,
                 log_level,
                 stdout_stderr,
                 use_fireworks,
                 separate_build_stdio):
        self.__config = config
        self.__tests = rgt_input_file.get_tests()
        self.__tasks = rgt_input_file.get_harness_tasks()
        self.__local_path_to_tests = rgt_input_file.get_path_to_tests()
        self.__apptests_dict = collections.OrderedDict()
        self.__app_subtests = []
        self.__log_level = log_level
        self.__myLogger = None
        self.__stdout_stderr = stdout_stderr
        self.__num_workers = 1
        self.__use_fireworks = use_fireworks
        self.__separate_build_stdio = separate_build_stdio
        self.__formAppTests()

        currenttime = time.localtime()
        time_stamp = time.strftime("%Y%m%d_%H%M%S",currenttime)
        self.__timestamp = time_stamp

        # Define a logger that streams to file.
        logger_name=Harness.LOGGER_NAME
        fh_filepath="./harness_log_files" + "." + self.__timestamp + "/" + Harness.LOGGER_NAME + "." + self.__timestamp + ".txt"
        logger_threshold = self.__log_level
        fh_threshold_log_level = "INFO"
        ch_threshold_log_level = "CRITICAL"
        self.__myLogger = rgt_logger_factory.create_rgt_logger(
                                     logger_name=logger_name,
                                     fh_filepath=fh_filepath,
                                     logger_threshold_log_level=logger_threshold,
                                     fh_threshold_log_level=fh_threshold_log_level,
                                     ch_threshold_log_level=ch_threshold_log_level)
    def __str__(self):
        message = ( "\n Local path to tests: " + self.__local_path_to_tests  + "\n"
                    "Tests: " + str(self.__tests) + "\n"
                    "Tasks: " + str(self.__tasks) + "\n")
        return message

    #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
    #                                                                 @
    # End of special methods                                          @
    #                                                                 @
    #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@


    #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
    #                                                                 @
    # Public methods.                                                 @
    #                                                                 @
    #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
    def run_me(self,
               my_effective_command_line=None,
               my_warning_messages=None):

        # Log the start of the harness.
        message = "Start of harness."
        self.__myLogger.doInfoLogging(message)

        # Log the effective command line"
        if my_effective_command_line:
            self.__myLogger.doInfoLogging(my_effective_command_line)

        # Log the command line warning messages
        if my_warning_messages:
            self.__myLogger.doInfoLogging(my_warning_messages)

        # Mark status as tasks not completed.
        self.__returnState = RgtState.ALL_TASKS_NOT_COMPLETED

        # Form a collection of applications with their subtests.
        self.__app_subtests = self.__formCollectionOfTests()

        # Run subtests
        if self.__use_fireworks:
            self.__run_fireworks()
        else:
            self.__run_subtests_asynchronously()

        # If we get to this point mark all task as completed.
        self.__returnState = RgtState.ALL_TASKS_COMPLETED

        message = "End of harness."
        self.__myLogger.doInfoLogging(message)
        return

    def getState(self):
        return self.__returnState

    def wait_for_completion_in_queue(self,timeout):
        """Waits 'timeout' minutes for all jobs to be completed in the queue.

        Parameters
        ----------
        timeout : float
            The maximum time to wait in minutes for the subtest cycle to complete.
        """
        future_to_appname = {}
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.__num_workers) as executor:
            for appname in self.__app_subtests.keys():
                future = executor.submit(apptest.wait_for_jobs_to_complete_in_queue,
                                         self.__config,
                                         self.__app_subtests[appname],
                                         timeout)

                future_to_appname[future] = appname

            for my_future in concurrent.futures.as_completed(future_to_appname):
                appname = future_to_appname[my_future]
                my_future_exception = my_future.exception()
                if my_future_exception:
                    message = "Application {} future for queue exception:\n{}".format(appname, my_future_exception)
                    self.__myLogger.doCriticalLogging(message)
                else:
                    message = "Application {} future for queue is completed.".format(appname)
                    self.__myLogger.doInfoLogging(message)
        return

    def didAllTestsPass(self):
        """Returns True if all tests have passed, otherwise False is returned.

        Returns
        -------
        bool
            A True return value means all tests have passed, otherwise a False value
            is returned.
        """
        ret_value = True
        for appname in self.__app_subtests.keys():
            for stests in self.__app_subtests[appname]:
                tmp_ret_value = stests.did_all_tests_pass(self.__config)
                ret_value = ret_value and tmp_ret_value

        return ret_value

    #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
    #                                                                 @
    # End of public methods.                                          @
    #                                                                 @
    #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@


    #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
    #                                                                 @
    # Private methods.                                                @
    #                                                                 @
    #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

    def __formAppTests(self):
        """ Sets up __apptests_dict. Keys are application name, values are list of test names. """
        application_names = set()
        for test in self.__tests:
            appname = test[0]
            testname = test[1]
            if appname not in application_names:
                application_names.add(appname)
                self.__apptests_dict[appname] = []
            self.__apptests_dict[appname].append(testname)

    def __doing_unit_testing(self):
        value = False
        if os.getenv('UNIT_TESTS_CWD'):
            value = True
            message = f"UNIT_TESTS_CWD: {value}"
            self.__myLogger.doInfoLogging(message)
        return value

    def __formCollectionOfTests(self):
        app_subtests = collections.OrderedDict()
        for (appname, tests) in self.__apptests_dict.items():
            if appname not in app_subtests:
                app_subtests[appname] = []
            for testname in tests:

                logger_name = appname + "." + testname + "." + self.__timestamp
                fh_filepath = "harness_log_files" + "." + self.__timestamp + "/" + appname + "/" + appname + "__" + testname +  ".logfile.txt"
                logger_threshold = self.__log_level
                fh_threshold_log_level = "INFO"
                ch_threshold_log_level = "CRITICAL"
                a_logger = rgt_logger_factory.create_rgt_logger(logger_name=logger_name,
                                      fh_filepath=fh_filepath,
                                      logger_threshold_log_level=logger_threshold,
                                      fh_threshold_log_level=fh_threshold_log_level,
                                      ch_threshold_log_level=ch_threshold_log_level)

                subtest = SubtestFactory.make_subtest(name_of_application=appname,
                                                      name_of_subtest=testname,
                                                      local_path_to_tests=self.__local_path_to_tests,
                                                      logger = a_logger,
                                                      tag=self.__timestamp)

                app_subtests[appname].append(subtest)

        return app_subtests

    def __run_subtests_asynchronously(self):
        future_to_appname = {}

        # Submit futures by means of thread pool.
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.__num_workers) as executor:
            for appname in self.__app_subtests.keys():
                future = executor.submit(apptest.do_application_tasks,
                                         self.__app_subtests[appname],
                                         self.__tasks,
                                         self.__stdout_stderr,
                                         self.__separate_build_stdio)
                future_to_appname[future] = appname

            # Log when all job tasks are initiated.
            for my_future in concurrent.futures.as_completed(future_to_appname):
                appname = future_to_appname[my_future]

                # Check if an exception has been raised
                my_future_exception = my_future.exception()
                if my_future_exception:
                    message = "Application {} future exception:\n{}".format(appname, my_future_exception)
                    self.__myLogger.doCriticalLogging(message)
                else:
                    message = "Application {} future is completed.".format(appname)
                    self.__myLogger.doInfoLogging(message)

            message = "All applications completed futures. Yahoo!!"
            self.__myLogger.doInfoLogging(message)

        return

    def __run_fireworks(self):
        from fireworks import Firework, Workflow, LaunchPad, ScriptTask

        # set up the LaunchPad
        launchpad = LaunchPad()

        cfg_file = self.__config.get_config_file()

        for (appname, tests) in self.__app_subtests.items():
            message = "Application " + appname + " has been submitted for running tasks."
            self.__myLogger.doInfoLogging(message)

            for subtest in tests:

                uid = subtest.get_harness_id()
                testname = subtest.getNameOfSubtest()
                task_suffix = f'{appname}.{testname}_@_{uid}'
                #print(f'Using task suffix: {task_suffix}')

                # create machine and run status files/directories for current subtest
                # (NOTE: working dir must be scripts_dir)
                scripts_dir = subtest.get_path_to_scripts()
                current_dir = os.getcwd()
                os.chdir(scripts_dir)
                subtest.create_test_status()
                ra_dir = subtest.create_test_runarchive()
                machine = MachineFactory.create_machine(self.__config, subtest)
                machine_name = machine.get_machine_name()
                os.chdir(current_dir)

                # create build FireWork
                taskname = f'OTH-BLD.{machine_name}.{task_suffix}'
                if self.__separate_build_stdio:
                    driver_cmd = f'test_harness_driver.py -C {cfg_file} --build --separate-build-stdio --scriptsdir {scripts_dir} --uniqueid {uid}'
                else:
                    driver_cmd = f'test_harness_driver.py -C {cfg_file} --build --scriptsdir {scripts_dir} --uniqueid {uid}'
                script_cmd = f'echo "Running: {driver_cmd}"; {driver_cmd} &> fwbuild.log'
                build_task = ScriptTask(script=script_cmd,
                                        store_stdout=True, store_stderr=True)
                category = f'{machine_name}-build'
                fw1 = Firework(build_task, fw_id=1, name=taskname,
                               spec={'_category':category, '_launch_dir':ra_dir})

                # create batch run FireWork
                taskname = f'OTH-RUN.{machine_name}.{task_suffix}'
                driver_cmd = f'test_harness_driver.py -C {cfg_file} --run --scriptsdir {scripts_dir} --uniqueid {uid}'
                script_cmd = f'echo "Running: {driver_cmd}"; {driver_cmd} &> fwrun.log'
                run_task = ScriptTask(script=script_cmd,
                                      store_stdout=True, store_stderr=True)
                rgt_test = machine.test_config
                replacements = rgt_test.get_test_replacements()
                job_overrides = {
                    'job_name' : replacements['__job_name__'],
                    'walltime' : replacements['__walltime__'],
                    'nodes'    : replacements['__nodes__']
                }
                if '__batch_queue__' in replacements.keys():
                    job_overrides['queue'] = replacements['__batch_queue__']
                if '__project_id__' in replacements.keys():
                    job_overrides['account'] = replacements['__project_id__']

                category = f'{machine_name}-run'
                fw2 = Firework(run_task, fw_id=2, name=taskname,
                               spec={'_category':category, '_launch_dir':ra_dir, '_queueadapter':job_overrides})

                # create check FireWork
                taskname = f'OTH-CHK.{machine_name}.{task_suffix}'
                driver_cmd = f'test_harness_driver.py -C {cfg_file} --check --scriptsdir {scripts_dir} --uniqueid {uid}'
                script_cmd = f'echo "Running: {driver_cmd}"; {driver_cmd} &> fwcheck.log'
                check_task = ScriptTask(script=script_cmd,
                                        store_stdout=True, store_stderr=True)
                category = f'{machine_name}-check'
                fw3 = Firework(check_task, fw_id=3, name=taskname,
                               spec={'_category':category, '_launch_dir':ra_dir})

                # make workflow and add it to the LaunchPad
                wfname = f'OTH-WF.{machine_name}.{task_suffix}'
                workflow = Workflow([fw1, fw2, fw3], {1: [2], 2: [3]}, name=wfname)
                launchpad.add_wf(workflow)

                message = "Added workflow " + wfname + "\n========\n"
                message += str(workflow.to_display_dict())
                self.__myLogger.doInfoLogging(message)

    #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
    #                                                                 @
    # End of private methods.                                         @
    #                                                                 @
    #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

