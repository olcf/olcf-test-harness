#!/usr/bin/env python
#
# Author: Veronica G. Vergara L.
#

from .base_machine import BaseMachine
import os
import re

class IBMpower8(BaseMachine):
    
    def __init__(self,name='IBM Power8',scheduler=None,jobLauncher=None,
                 numNodes=0,numSocketsPerNode=0,numCoresPerSocket=0,rgt_test_input_file="rgt_test_input.txt"):
        BaseMachine.__init__(self,name,scheduler,jobLauncher,numNodes,
                             numSocketsPerNode,numCoresPerSocket,rgt_test_input_file)
        self.__rgt_test_input = None

    def read_rgt_test_input(self):
        total_processes = None
        processes_per_node = None
        processes_per_socket = None
        jobname = None
        batchqueue = None
        walltime = None
        if os.path.isfile(self.get_rgt_input_file_name()):
            print("Reading input file from Power8")

            # Read the required parameters from RGT test input
            total_processes_pattern = "total_processes"
            processes_per_node_pattern = "processes_per_node"
            processes_per_socket_pattern = "processes_per_socket"
            jobname_pattern = "jobname"
            batchqueue_pattern = "batchqueue"
            walltime_pattern = "walltime"
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
                    jobname = words[1].strip('\n')
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
                    batchqueue = words[1].strip('\n')
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

        else:
            print("No input found. Provide your own build, submit, check, and report scripts")

    def make_batch_script(self):
        print("Making batch script for Power8")
        self.read_rgt_test_input()
        return

    def submit_batch_script(self):
        print("Submitting batch script for Power8")
        return

if __name__ == "__main__":
    print('This is the IBM Power8 class')
