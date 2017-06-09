#!/usr/bin/env python3
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
        self.__buildscriptname = None
        self.__checkscriptname = None
        self.__reportscriptname = None
        self.__executablename = None

    def set_test_parameters(self,total_processes, processes_per_node, processes_per_socket, jobname, batchqueue, walltime, batchfilename, buildscriptname, checkscriptname, executablename, reportscriptname):
        self.__total_processes = total_processes
        self.__processes_per_node = processes_per_node
        self.__processes_per_socket = processes_per_socket
        self.__jobname = jobname
        self.__batchqueue = batchqueue
        self.__walltime = walltime
        self.__batchfilename = batchfilename
        self.__buildscriptname = buildscriptname
        self.__checkscriptname = checkscriptname
        self.__reportscriptname = reportscriptname
        self.__executablename = executablename

    def get_batchfilename(self):
        return self.__batchfilename

    def get_buildscriptname(self):
        return self.__buildscriptname

    def get_checkscriptname(self):
        return self.__checkscriptname

    def get_reportscriptname(self):
        return self.__reportscriptname

    def get_executablename(self):
        return self.__executablename

    def get_jobname(self):
        return self.__jobname

    def get_walltime(self):
        return str(self.__walltime)

    def get_batchqueue(self):
        return self.__batchqueue

    def get_total_processes(self):
        return str(self.__total_processes)

    def get_processes_per_node(self):
        return str(self.__processes_per_node)

    def get_processes_per_socket(self):
        return str(self.__processes_per_socket)

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
        print("buildscriptname = " + self.__buildscriptname)
        print("checkscriptname = " + self.__checkscriptname)
        print("reportscriptname = " + self.__reportscriptname)
        print("executablename = " + self.__executablename)

if __name__ == "__main__":
    print('This is the RgtTest class')
