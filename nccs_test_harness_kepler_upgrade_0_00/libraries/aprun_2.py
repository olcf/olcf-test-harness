#!/usr/bin/env python3

import re


class nodelist:
    def __init__(self):
        pass

class baseaprun:
    def __init__(self):
        self.__stringpattern1 = "total number of sockets"
        self.__re1 = re.compile(self.__stringpattern1 + "$")

        self.__stringpattern2 = "number of cores per socket"
        self.__re2 = re.compile(self.__stringpattern2 + "$")

        self.__delimiter = "="

        self.__filename = "size.txt"

        self.__total_number_of_sockets = 0
        self.__number_of_cores_per_socket = 0
        self.__number_of_processors = 0
        self.__tag = ""

        #Read all the lines of the file.
        fileobj = open(self.__filename,'r')
        filerecords = fileobj.readlines()
        fileobj.close()

        #Parse for the total number of sockets.
        for record1 in  filerecords:
            words = record1.split(self.__delimiter)
            words[0] = words[0].strip().lower()
            if self.__re1.match(words[0]):
                self.__total_number_of_sockets = int(words[1])
                break


        #Parse for the number of cores per socket.
        for record1 in  filerecords:
            words = record1.split(self.__delimiter)
            words[0] = words[0].strip().lower()
            if self.__re2.match(words[0]):
                self.__number_of_cores_per_socket= int(words[1])
                break

        #Compute the number of processors.
        self.__number_of_processors = self.__total_number_of_sockets*self.__number_of_cores_per_socket

        #Make the job tag.
        string1 = str(self.__total_number_of_sockets)
        startindex = 0
        finalindex = 4
        len1 = len(string1)
        len2 = finalindex - (len1 - 1)
        self.__tag = string1 + len2*"_"

        startindex=0
        finalindex=4
        string2 = str(self.__number_of_processors)
        len1 = len(string2)
        len2 = finalindex - (len1 -1)
        self.__tag = self.__tag + string2 + len2*"_"
       
        startindex=0
        finalindex=1
        string3 = str(self.__number_of_cores_per_socket)
        len1 = len(string3)
        len2 = finalindex - (len1 - 1)
        self.__tag = self.__tag + string3 + len2*"_"

    def get_problem_size(self):
        return (self.__total_number_of_sockets,self.__number_of_cores_per_socket,self.__number_of_processors)

    def get_running_nm_procs(self):
        return self.__number_of_processors

    def get_number_of_cores_per_socket(self):
        return self.__number_of_cores_per_socket

    def get_job_tag(self):
        return self.__tag

    def get_total_number_of_sockets(self):
        return self.__total_number_of_sockets

    def get_allocated_nm_procs(self):
        return self.__maximum_number_processors

    def set_allocated_nm_procs(self,nm1):
        self.__maximum_number_processors = nm1

class quadcore(baseaprun):
    #Maximum cores per socket.
    MAX_CORES_PER_SOCKET = 4

    def __init__(self):
        baseaprun.__init__(self)

        #Compute the maximum number of processors.
        maximum_number_processors = self.get_total_number_of_sockets()*quadcore.MAX_CORES_PER_SOCKET
        self.set_allocated_nm_procs(maximum_number_processors)


class dualcore(baseaprun):
    #Maximum cores per socket.
    MAX_CORES_PER_SOCKET = 2

    def __init__(self):
        self.maximum_number_processors = 0
        baseaprun.__init__(self)

        #Compute the maximum number of processors.
        maximum_number_processors = self.get_total_number_of_sockets()*dualcore.MAX_CORES_PER_SOCKET
        self.set_allocated_nm_procs(maximum_number_processors)
