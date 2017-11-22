#!/usr/bin/env python
#
# Author: Veronica G. Vergara L.
#

from .base_machine import BaseMachine
from .rgt_test import RgtTest
import os
import re

class IBMpower9(BaseMachine):
    
    def __init__(self,
                 name='IBM Power9',
                 scheduler=None,
                 jobLauncher=None,
                 numNodes=1,
                 numSocketsPerNode=2,
                 numCoresPerSocket=21,
                 rgt_test_input_file="rgt_test_input.txt",
                 workspace=None,
                 harness_id=None,
                 scripts_dir=None):
        BaseMachine.__init__(self,
                             name,
                             scheduler,
                             jobLauncher,
                             numNodes,
                             numSocketsPerNode,
                             numCoresPerSocket,
                             rgt_test_input_file,
                             workspace,harness_id,
                             scripts_dir)
        self.__rgt_test_input = None
        self.__rgt_test = RgtTest()

        #self.read_rgt_test_input()
        self.read_custom_rgt_test_input()

    def read_custom_rgt_test_input(self):

        template_dict = {}

        if os.path.isfile(self.get_rgt_input_file_name()):
            print("Reading custom key-value pairs from Power9 input")

            # Read the custom parameters from RGT test input
            delimiter = "="

            fileobj = open(self.get_rgt_input_file_name())
            filerecords = fileobj.readlines()
            fileobj.close()

            for record in filerecords:
                (k,v) = record.split('=')
                template_dict[k.strip().lower()] = v.strip()

        # Variables needed by the harness
        template_dict["rgtenvironmentalfile"] = os.environ["RGT_ENVIRONMENTAL_FILE"]
        template_dict["nccstestharnessmodule"] = os.environ["RGT_NCCS_TEST_HARNESS_MODULE"]
        template_dict["resultsdir"] = self.get_rgt_results_dir()
        template_dict["workdir"] = self.get_rgt_workdir()
        template_dict["startingdirectory"] = self.get_rgt_scripts_dir()
        template_dict["unique_id_string"] = self.get_rgt_harness_id()

        print(template_dict)

        self.__rgt_test.set_custom_test_parameters(template_dict)
        self.__rgt_test.print_custom_test_parameters()
        self.__rgt_test.check_builtin_parameters()

        self.__rgt_test.append_to_template_dict("pathtoexecutable",os.path.join(self.get_rgt_workspace(),"build_directory/bin",self.__rgt_test.get_executablename()))
        self.__rgt_test.append_to_template_dict("joblaunchcommand",self.get_jobLauncher_command(self.__rgt_test.get_value_from_template_dict("pathtoexecutable")))

    def read_rgt_test_input(self):
        total_processes = None
        processes_per_node = None
        processes_per_socket = None
        jobname = None
        batchqueue = None
        walltime = None
        batchfilename = None
        buildscriptname = None
        checkscriptname = None
        reportscriptname = None
        testinputfile = None

        if os.path.isfile(self.get_rgt_input_file_name()):
            print("Reading input file from Power9")

            # Read the required parameters from RGT test input
            total_processes_pattern = "total_processes"
            processes_per_node_pattern = "processes_per_node"
            processes_per_socket_pattern = "processes_per_socket"
            jobname_pattern = "jobname"
            batchqueue_pattern = "batchqueue"
            walltime_pattern = "walltime"
            batchfilename_pattern = "batchfilename"
            buildscriptname_pattern = "buildscriptname"
            checkscriptname_pattern = "checkscriptname"
            reportscriptname_pattern = "reportscriptname"
            executablename_pattern = "executablename"
            testinputfile_pattern = "testinputfile"
            delimiter = "="

            fileobj = open(self.get_rgt_input_file_name())
            filerecords = fileobj.readlines()
            fileobj.close()

            # Find the number of total processes for the test
            temp_re = re.compile(total_processes_pattern + "$")
            for record in filerecords:
                words = record.split(delimiter)
                words[0] = words[0].strip().lower()
                if temp_re.match(words[0]):
                    total_processes = int(words[1])
                    break
            if total_processes:
                print("Found total_processes is " + str(total_processes) + " in IBM Power 8 machine")
            else:
                print("No total_processes requested in IBM Power 8 machine")

            # Find the number of processes per node the test
            temp_re = re.compile(processes_per_node_pattern + "$")
            for record in filerecords:
                words = record.split(delimiter)
                words[0] = words[0].strip().lower()
                if temp_re.match(words[0]):
                    processes_per_node = int(words[1])
                    break
            if processes_per_node:
                print("Found processes_per_node is " + str(processes_per_node) + " in IBM Power 8 machine")
            else:
                print("No processes_per_node requested in IBM Power 8 machine")

            # Find the number of processes per socket the test
            temp_re = re.compile(processes_per_socket_pattern + "$")
            for record in filerecords:
                words = record.split(delimiter)
                words[0] = words[0].strip().lower()
                if temp_re.match(words[0]):
                    processes_per_socket = int(words[1])
                    break
            if processes_per_socket:
                print("Found processes_per_socket is " + str(processes_per_socket) + " in IBM Power 8 machine")
            else:
                print("No processes_per_socket requested in IBM Power 8 machine")


            # Find the job name the test
            temp_re = re.compile(jobname_pattern + "$")
            for record in filerecords:
                words = record.split(delimiter)
                words[0] = words[0].strip().lower()
                if temp_re.match(words[0]):
                    jobname = words[1].strip('\n').strip()
                    break
            if jobname:
                print("Found jobname is " + jobname + " in IBM Power 8 machine")
            else:
                print("No jobname provided in IBM Power 8 machine")

            # Find the queue to use for the test
            temp_re = re.compile(batchqueue_pattern + "$")
            for record in filerecords:
                words = record.split(delimiter)
                words[0] = words[0].strip().lower()
                if temp_re.match(words[0]):
                    batchqueue = words[1].strip('\n').strip()
                    break
            if batchqueue:
                print("Found batchqueue is " + batchqueue + " in IBM Power 8 machine")
            else:
                print("No batchqueue provided in IBM Power 8 machine")

            # Find the walltime to use for the test
            temp_re = re.compile(walltime_pattern + "$")
            for record in filerecords:
                words = record.split(delimiter)
                words[0] = words[0].strip().lower()
                if temp_re.match(words[0]):
                    walltime = int(words[1])
                    break
            if walltime:
                print("Found walltime is " + str(walltime) + " in IBM Power 8 machine")
            else:
                print("No walltime provided in IBM Power 8 machine")

            # Find the name for the batch submission file to use for the test
            temp_re = re.compile(batchfilename_pattern + "$")
            for record in filerecords:
                words = record.split(delimiter)
                words[0] = words[0].strip().lower()
                if temp_re.match(words[0]):
                    batchfilename = words[1].strip('\n').strip()
                    break
            if batchfilename:
                print("Found batchfilename is " + batchfilename + " in IBM Power 8 machine")
            else:
                print("No batchfilename provided in IBM Power 8 machine")

            # Find the name for the build script file to use to build the application
            temp_re = re.compile(buildscriptname_pattern + "$")
            for record in filerecords:
                words = record.split(delimiter)
                words[0] = words[0].strip().lower()
                if temp_re.match(words[0]):
                    buildscriptname = words[1].strip('\n').strip()
                    break
            if buildscriptname:
                print("Found buildscriptname is " + buildscriptname + " in IBM Power 8 machine")
            else:
                print("No buildscriptname provided in IBM Power 8 machine")

            # Find the name for the check script file to use to verify the test results
            temp_re = re.compile(checkscriptname_pattern + "$")
            for record in filerecords:
                words = record.split(delimiter)
                words[0] = words[0].strip().lower()
                if temp_re.match(words[0]):
                    checkscriptname = words[1].strip('\n').strip()
                    break
            if checkscriptname:
                print("Found checkscriptname is " + checkscriptname + " in IBM Power 8 machine")
            else:
                print("No checkscriptname provided in IBM Power 8 machine")

            # Find the name for the report script file to use to log results
            temp_re = re.compile(reportscriptname_pattern + "$")
            for record in filerecords:
                words = record.split(delimiter)
                words[0] = words[0].strip().lower()
                if temp_re.match(words[0]):
                    reportscriptname = words[1].strip('\n').strip()
                    break
            if reportscriptname:
                print("Found reportscriptname is " + reportscriptname + " in IBM Power 8 machine")
            else:
                print("No reportscriptname provided in IBM Power 8 machine")

            # Find the name for the executable to use to launch the test
            temp_re = re.compile(executablename_pattern + "$")
            for record in filerecords:
                words = record.split(delimiter)
                words[0] = words[0].strip().lower()
                if temp_re.match(words[0]):
                    executablename = words[1].strip('\n').strip()
                    break
            if executablename:
                print("Found executablename is " + executablename + " in IBM Power 8 machine")
            else:
                print("No executablename provided in IBM Power 8 machine")
                
            # Find the name for the input of the test
            temp_re = re.compile(testinputfile_pattern + "$")
            for record in filerecords:
                words = record.split(delimiter)
                words[0] = words[0].strip().lower()
                if temp_re.match(words[0]):
                    testinputfile = words[1].strip('\n').strip()
                    break
            if testinputfile:
                print("Found testinputfile is " + testinputfile + " in IBM Power 8 machine" )
            else:
                print("No testinputfile provided in IBM Power 8 machine")


            self.__rgt_test.set_test_parameters(total_processes, processes_per_node, processes_per_socket, 
                                                jobname, batchqueue, walltime, batchfilename, buildscriptname, 
                                                checkscriptname, executablename, reportscriptname, testinputfile)
            self.__rgt_test.print_test_parameters()
        else:
            print("No input found. Provide your own build, submit, check, and report scripts")

    def get_jobLauncher_command(self,path_to_executable):
        print("Building jobLauncher command for Power9")
        jobLauncher_command = self.build_jobLauncher_command(self.__rgt_test.get_template_dict())
        return jobLauncher_command

    def make_custom_batch_script(self):
        print("Making batch script for Power9 using template called " + self.get_scheduler_template_file_name())
        templatefileobj = open(self.get_scheduler_template_file_name(),"r")
        templatelines = templatefileobj.readlines()
        templatefileobj.close()

        template_dict = self.__rgt_test.get_template_dict()
        replace_dict = {}

        for (k,v) in template_dict.items():
            print("key = ",k,"value = ",v)
            newk = "__" + k + "__"
            replace_dict[newk] = v

        fileobj = open(self.__rgt_test.get_batchfilename(),"w")
        for record in templatelines:
            for (k,v) in replace_dict.items():
                re_temp = re.compile(k)
                record = re_temp.sub(v,record)
            fileobj.write(record)
        fileobj.close()

        print("")
        print("Replacement Dictionary")
        print(replace_dict)

    def make_batch_script(self):
        print("Making batch script for Power9 using template called " + self.get_scheduler_template_file_name())
        templatefileobj = open(self.get_scheduler_template_file_name(),"r")
        templatelines = templatefileobj.readlines()
        templatefileobj.close()

        rgt_array = [
            (re.compile("__jobname__"),self.__rgt_test.get_jobname()),
            (re.compile("__walltime__"),self.__rgt_test.get_walltime()),
            (re.compile("__batchqueue__"),self.__rgt_test.get_batchqueue()),
            (re.compile("__total_processes__"),self.__rgt_test.get_total_processes()),
            (re.compile("__processes_per_node__"),self.__rgt_test.get_processes_per_node()),
            (re.compile("__rgtenvironmentalfile__"),os.environ["RGT_ENVIRONMENTAL_FILE"]),
            (re.compile("__nccstestharnessmodule__"),os.environ["RGT_NCCS_TEST_HARNESS_MODULE"]),
            (re.compile("__resultsdir__"),self.get_rgt_results_dir()),
            (re.compile("__workdir__"),self.get_rgt_workdir()),
            (re.compile("__startingdirectory__"),self.get_rgt_scripts_dir()),
            (re.compile("__unique_id_string__"),self.get_rgt_harness_id()),
            (re.compile("__batchfilename__"),self.__rgt_test.get_batchfilename()),
            (re.compile("__pathtoexecutable__"),os.path.join(self.get_rgt_workspace(),"build_directory/bin",self.__rgt_test.get_executablename())),
            (re.compile("__joblaunchcommand__"),self.get_jobLauncher_command(os.path.join(self.get_rgt_workspace(),"build_directory",self.__rgt_test.get_executablename()))),
            (re.compile("__testinputfile__"),self.__rgt_test.get_testinputfile()),
           ]

        fileobj = open(self.__rgt_test.get_batchfilename(),"w")
        for record in templatelines:
            for (re_temp,value) in rgt_array:
                record = re_temp.sub(value,record)
            fileobj.write(record)
        fileobj.close()

        return

    def build_executable(self):
        print("Building executable on Power9 using build script " + self.__rgt_test.get_buildscriptname())
        return self.start_build_script(self.__rgt_test.get_buildscriptname())

    def submit_batch_script(self):
        print("Submitting batch script for Power9")
        submit_exit_value = self.submit_to_scheduler(self.__rgt_test.get_batchfilename(),self.get_rgt_harness_id())
        print("Submitting " + self.__rgt_test.get_batchfilename() + " submit_exit_value = " + str(submit_exit_value))
        return submit_exit_value

    def check_executable(self):
        print("Running check executable script on Power9 using check script " + self.__rgt_test.get_checkscriptname())
        return self.check_results(self.__rgt_test.get_checkscriptname())

    def report_executable(self):
        print("Running report executable script on Power9 using report script " + self.__rgt_test.get_reportscriptname())
        return self.start_report_script(self.__rgt_test.get_reportscriptname())

if __name__ == "__main__":
    print('This is the IBM Power9 class')
