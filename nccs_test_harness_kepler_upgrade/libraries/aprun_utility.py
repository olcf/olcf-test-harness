#!/usr/bin/env python

import re

class aprun:
    def __init__(self):
        self.__stringpattern1 = "total number of processors"
        self.__re1 = re.compile(self.__stringpattern1 + "$")
        self.__stringpattern2 = "number of processors"
        self.__re2 = re.compile(self.__stringpattern2 + "$")
        self.__stringpattern3 = "depth of processors"
        self.__re3 = re.compile(self.__stringpattern3 + "$")
        self.__delimiter = "="
        self.__filename = "size.txt"
        self.__total_number_of_processors = 0
        self.__nm_procs = 0
        self.__depth = None
        self.__tag = ""

        #Read all the lines of the file.
        fileobj = open(self.__filename,'r')
        filerecords = fileobj.readlines()
        fileobj.close()

        #Parse for the total number of processors.
        for record1 in  filerecords:
            words = record1.split(self.__delimiter)
            words[0] = words[0].strip().lower()
            if self.__re1.match(words[0]):
                self.__total_number_of_processors = int(words[1])
                break


        #Parse for the number of processors.
        for record1 in  filerecords:
            words = record1.split(self.__delimiter)
            words[0] = words[0].strip().lower()
            if self.__re2.match(words[0]):
                self.__nm_procs = int(words[1])
                break

        #Parse for the depth of the processors
        for record1 in  filerecords:
            words = record1.split(self.__delimiter)
            words[0] = words[0].strip()
            words[0] = words[0].lower()
            if self.__re3.match(words[0]):
                self.__depth = int(words[1])
                break

        #Make the job tag.
        string1 = str(self.__total_number_of_processors)
        startindex = 0
        finalindex = 4
        len1 = len(string1)
        len2 = finalindex - (len1 - 1)
        self.__tag = string1 + len2*"_"

        startindex=0
        finalindex=4
        string2 = str(self.__nm_procs)
        len1 = len(string2)
        len2 = finalindex - (len1 -1)
        self.__tag = self.__tag + string2 + len2*"_"
       
        startindex=0
        finalindex=1
        string3 = str(self.__depth)
        len1 = len(string3)
        len2 = finalindex - (len1 - 1)
        self.__tag = self.__tag + string3 + len2*"_"

    def get_problem_size(self):
        return (self.__total_number_of_processors,self.__nm_procs,self.__depth)

    def get_total_number_of_procs(self):
        return self.__total_number_of_processors

    def get_nm_procs(self):
        return self.__nm_procs

    def get_depth(self):
        return self.__depth

    def get_job_tag(self):
        return self.__tag

class aprun2:
    #Maximum cores per socket.
    MAX_CORES_PER_SOCKET = 4


    def __init__(self):
        self.__stringpattern1 = "total number of sockets"
        self.__re1 = re.compile(self.__stringpattern1 + "$")

        self.__stringpattern2 = "number of cores per socket"
        self.__re2 = re.compile(self.__stringpattern2 + "$")

        self.__delimiter = "="

        self.__filename = "size.txt"

        self.__total_number_of_sockets = 0
        self.__number_of_cores_per_socket = 0
        self.__maximum_number_processors = 0
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

        #Compute the maximum number of processors.
        self.__maximum_number_processors = self.__total_number_of_sockets*aprun2.MAX_CORES_PER_SOCKET

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

    def get_allocated_nm_procs(self):
        return self.__maximum_number_processors

    def get_running_nm_procs(self):
        return self.__number_of_processors

    def get_number_of_cores_per_socket(self):
        return self.__number_of_cores_per_socket

    def get_job_tag(self):
        return self.__tag

class quadcore:
    #Maximum cores per socket.
    MAX_CORES_PER_SOCKET = 4

class aprun(quadcore):

    def __init__(self):
        self.__stringpattern1 = "total number of sockets"
        self.__re1 = re.compile(self.__stringpattern1 + "$")

        self.__stringpattern2 = "number of cores per socket"
        self.__re2 = re.compile(self.__stringpattern2 + "$")

        self.__delimiter = "="

        self.__filename = "size.txt"

        self.__total_number_of_sockets = 0
        self.__number_of_cores_per_socket = 0
        self.__maximum_number_processors = 0
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

        #Compute the maximum number of processors.
        self.__maximum_number_processors = self.__total_number_of_sockets*aprun2.MAX_CORES_PER_SOCKET

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

    def get_allocated_nm_procs(self):
        return self.__maximum_number_processors

    def get_running_nm_procs(self):
        return self.__number_of_processors

    def get_number_of_cores_per_socket(self):
        return self.__number_of_cores_per_socket

    def get_job_tag(self):
        return self.__tag

class nodelist:
    def __init__(self):
        pass
