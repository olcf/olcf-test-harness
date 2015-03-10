#!/usr/bin/env python
import os
import re

class pop_utility:
    def __init__(self):
        self.__stringpattern1 = "pop number of processors in x dimension"
        self.__re1 = re.compile(self.__stringpattern1 + "$")
        self.__stringpattern2 = "pop number of processors in y dimension"
        self.__re2 = re.compile(self.__stringpattern2 + "$")
        self.__stringpattern3 = "number of cores per socket"
        self.__re3 = re.compile(self.__stringpattern3 + "$")
        self.__delimiter = "="
        self.__filename = "size.txt"
        self.__archdir = ""
        self.__nm_procx = 0
        self.__nm_procy = 0
        self.__nm_procs = 0
        self.__procs_per_node = 4

        #Read all the lines of the file.
        fileobj = open(self.__filename,'r')
        filerecords = fileobj.readlines()
        fileobj.close()

        #Parse for processors in the x dimension.
        for record1 in  filerecords:
            words = record1.split(self.__delimiter)
            words[0] = words[0].strip().lower()
            if self.__re1.match(words[0]):
                self.__nm_procx = int(words[1])
                break

        #Parse for processors in the y dimension.
        for record1 in  filerecords:
            words = record1.split(self.__delimiter)
            words[0] = words[0].strip().lower()
            if self.__re2.match(words[0]):
                self.__nm_procy = int(words[1])
                break

        #Parse for processors per node
        for record1 in  filerecords:
            words = record1.split(self.__delimiter)
            words[0] = words[0].strip().lower()
            if self.__re3.match(words[0]):
                self.__procs_per_node = int(words[1])
                break

        #Compute the number of processors.
        self.__nm_procs = (self.__nm_procx)*(self.__nm_procy)

        #Set the arch dir variable.
        stringvar1 = "jaguar_mpi_" + str(self.__nm_procx) +"x" + str(self.__nm_procy)
        self.__archdir = stringvar1
        os.putenv("ARCHDIR",stringvar1) 

    def get_problem_size(self):
        return (self.__nm_procx,self.__nm_procy)

    def get_nm_procs(self):
        return self.__nm_procs

    def get_arch_dir(self):
        return self.__archdir

    def get_depth(self):
        return self.__procs_per_node
