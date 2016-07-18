#!/usr/bin/env python
#
# Author: Veronica G. Vergara L.
#


class RgtTest():

    def __init__(self):
        self.__total_processes = None
        self.__processes_per_node = None
        self.__processes_per_socket = None
        self.__jobname = None
        self.__batchqueue = None
        self.__walltime = None
        self.__batchfilename = None

    def set_test_parameters(self,total_processes, processes_per_node, processes_per_socket, jobname, batchqueue, walltime, batchfilename):
        self.__total_processes = total_processes
        self.__processes_per_node = processes_per_node
        self.__processes_per_socket = processes_per_socket
        self.__jobname = jobname
        self.__batchqueue = batchqueue
        self.__walltime = walltime
        self.__batchfilename = batchfilename

    def get_batchfilename(self):
        return self.__batchfilename

    def get_jobname(self):
        return self.__jobname

    def get_walltime(self):
        return str(self.__walltime)

    def get_batchqueue(self):
        return self.__batchqueue

    def get_total_processes(self):
        return str(self.__total_processes)

    def print_test_parameters(self):
        print("RGT Test parameters")
        print("===================")
        print("total_processes = " + str(self.__total_processes))
        print("processes_per_node = " + str(self.__processes_per_node))
        print("processes_per_socket = " + str(self.__processes_per_socket))
        print("jobname = " + self.__jobname)
        print("batchqueue = " + self.__batchqueue)
        print("walltime = " + str(self.__walltime))
        print("batchfilename = " + self.__batchfilename)

if __name__ == "__main__":
    print('This is the RgtTest class')
