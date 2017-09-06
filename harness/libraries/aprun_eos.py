#!/usr/bin/env python3

import re

class baseaprun:
    #-----------------------------------------------------
    # Define the mpi run command for alps.               -
    #                                                    -
    #-----------------------------------------------------
    MPIRUN = "aprun"

    def __init__(self):
        #-----------------------------------------------------
        # Define the name of the input file that             -
        # contains the job size configuration.               -
        #                                                    -
        #-----------------------------------------------------
        self.__filename = "size.txt"

        #-----------------------------------------------------
        # Define the text patterns for tokenizing and        -
        # parsing the input file.                            -
        #                                                    -
        #-----------------------------------------------------
        self.__stringpattern1 = "number of eos cores per numa"
        self.__re1 = re.compile(self.__stringpattern1 + "$")

        self.__stringpattern2 = "number of cores per eos socket"
        self.__re2 = re.compile(self.__stringpattern2 + "$")

        self.__stringpattern3 = "number of threads per mpi task"
        self.__re3 = re.compile(self.__stringpattern3 + "$")

        self.__stringpattern4 = "number of nodes"
        self.__re4 = re.compile(self.__stringpattern4 + "$")

        self.__delimiter = "="


        #-----------------------------------------------------
        # Initialize the attributes of the aprun class.      -
        #                                                    -
        #-----------------------------------------------------
        self.__total_number_of_nodes = None
        self.__number_of_eos_sockets_per_node = 1
        self.__number_of_accelerator_sockets_per_node = 1
        self.__numberOfCoresPerEosSocket = None
        self.__numberOfCoresPerEosNuma=None
        self.__threads_per_mpi_task = None
        self.__total_number_of_sockets = None
        self.__number_of_processors = None
        self.__number_mpi_tasks = None
        self.__tag = ""

        #-----------------------------------------------------
        # Read all the lines of the file and store in a list -
        # named "filerecords".                               -
        #                                                    -
        #-----------------------------------------------------
        fileobj = open(self.__filename,'r')
        filerecords = fileobj.readlines()
        fileobj.close()

        #-----------------------------------------------------
        # Parse for the total number of nodes.               -
        #                                                    -
        #-----------------------------------------------------
        for record1 in  filerecords:
            words = record1.split(self.__delimiter)
            words[0] = words[0].strip().lower()
            if self.__re4.match(words[0]):
                self.__total_number_of_nodes = int(words[1])
                break


        #-----------------------------------------------------
        # Parse for the number of eos cores per numa  -
        #                                                    -
        #-----------------------------------------------------
        for record1 in  filerecords:
            words = record1.split(self.__delimiter)
            words[0] = words[0].strip().lower()
            if self.__re1.match(words[0]):
                self.__numberOfCoresPerEosNuma = int(words[1])
                break


        #-----------------------------------------------------
        # Parse for the number of cores per socket.          -
        #                                                    -
        #-----------------------------------------------------
        for record1 in  filerecords:
            words = record1.split(self.__delimiter)
            words[0] = words[0].strip().lower()
            if self.__re2.match(words[0]):
                self.__numberOfCoresPerEosSocket= int(words[1])
                break


        #-----------------------------------------------------
        # Parse for the number of threads per core.          -
        #                                                    -
        #-----------------------------------------------------
        for record1 in  filerecords:
            words = record1.split(self.__delimiter)
            words[0] = words[0].strip()
            words[0] = words[0].lower()
            if self.__re3.match(words[0]):
                self.__threads_per_mpi_task = int(words[1])
                break


    def get_problem_size(self):
        return (self.__total_number_of_nodes,
                self.__numberOfCoresPerEosNuma,
                self.__numberOfCoresPerEosSocket,
                self.__number_of_processors,
                self.__threads_per_mpi_task)

    def get_number_of_running_procs(self):
        return self.__number_of_processors

    def set_number_of_running_procs(self,nm1):
        self.__number_of_processors = nm1  

    def get_number_of_nodes(self):
        return self.__total_number_of_nodes

    def set_number_of_nodes(self,nm1):
        nm1 = self.__total_number_of_nodes

    def get_number_of_cores_per_eos_numa(self):
        return self.__numberOfCoresPerEosNuma

    def get_number_of_eos_sockets_per_node(self):
        return self.__number_of_eos_sockets_per_node

    def getNumberOfCoresPerEosSocket(self):
        return self.__numberOfCoresPerEosSocket

    def get_job_tag(self):
        return self.__tag

    def get_total_number_of_sockets(self):
        return self.__total_number_of_sockets

    def get_allocated_nm_procs(self):
        return self.__maximum_number_processors

    def set_allocated_nm_procs(self,nm1):
        self.__maximum_number_processors = nm1

    def get_mpirun_command(self):
        return baseaprun.MPIRUN

    def get_threads_per_mpi_task(self):
        return self.__threads_per_mpi_task


    def get_job_launch_command(self):
        cmmd = baseaprun.MPIRUN 
        cmmd = cmmd + " -n " + str(self.get_number_of_running_procs()) + " "
        cmmd = cmmd + " -S " + str(self.get_number_of_cores_per_eos_numa()) + " "
        return cmmd

    def get_feature_option(self):
        return eos_16_core_depracated.FEATURE



class eos_16_core(baseaprun):
    #-----------------------------------------------------
    # Define the maximum number of cores per socket.     -
    # Define the feature for this node.                  -
    #                                                    -
    #-----------------------------------------------------
    MAX_CORES_PER_NODE = 16
    MAX_SOCKETS_PER_NODE= 2
    MAX_INTERLAGOS_SOCKETS_PER_NODE = 1
    MAX_ACCELERATOR_SOCKETS_PER_NODE = 1

    MAX_NUMA_PER_INTERLAGOS_SOCKET = 2
    MAX_CORES_PER_NODE = 16
    MAX_CORES_PER_INTERLAGOS_SOCKET = 16
    MAX_CORES_PER_INTERLAGOS_NUMA = 8
    FEATURE = None

    def __init__(self):
        baseaprun.__init__(self)

        #-----------------------------------------------------
        # Compute the number of cores that the we            - 
        # are running on, job size, etc.                     -
        #-----------------------------------------------------
        maximum_number_processors = 0
        nm_running_procs = 0
        job_tag = ""

        if self.get_number_of_nodes():
            nm_running_procs = self.get_number_of_nodes()*self.get_number_of_eos_sockets_per_node()*self.getNumberOfCoresPerEosSocket()
            self.set_number_of_running_procs(nm_running_procs)

            #-----------------------------------------------------
            # Compute the maximum number of processors.          -
            #                                                    -
            #-----------------------------------------------------
            maximum_number_processors = self.get_number_of_nodes()*eos_16_core.MAX_CORES_PER_NODE
            self.set_allocated_nm_procs(maximum_number_processors)

            #-----------------------------------------------------
            # Make the job tag.                                  -
            #                                                    -
            #-----------------------------------------------------
            string1 = str(self.get_number_of_nodes())
            finalindex = 4
            len1 = len(string1)
            len2 = finalindex - (len1 - 1)
            job_tag = string1 + len2*"_"

            finalindex=4
            string2 = str(self.get_number_of_eos_sockets_per_node())
            len1 = len(string2)
            len2 = finalindex - (len1 -1)
            job_tag = job_tag + string2 + len2*"_"
       
            finalindex=1
            string3 = str(self.get_threads_per_mpi_task())
            len1 = len(string3)
            len2 = finalindex - (len1 - 1)
            job_tag = job_tag + string3 + len2*"_"

            self.__tag = job_tag

    def get_job_launch_command(self):
        cmmd = baseaprun.MPIRUN 
        cmmd = cmmd + " -n " + str(self.get_number_of_running_procs()) + " "
        cmmd = cmmd + " -S " + str(self.get_number_of_cores_per_eos_numa()) + " "
        return cmmd

    def get_feature_option(self):
        return eos_16_core.FEATURE

