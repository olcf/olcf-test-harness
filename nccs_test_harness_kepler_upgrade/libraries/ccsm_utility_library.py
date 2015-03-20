#!/usr/bin/env python
import os
import re
import glob

class ccsm_utility:
    shortname = { "1.9x2.5_gx1v5" : "f19_g15",
                }
    def __init__(self):
        self.__stringpattern1 = "ccsmmachine"
        self.__re1 = re.compile(self.__stringpattern1 + "$")

        self.__stringpattern2 = "ccsmres"
        self.__re2 = re.compile(self.__stringpattern2 + "$")

        self.__stringpattern3 = "ccsmtest"
        self.__re3 = re.compile(self.__stringpattern3 + "$")

        self.__stringpattern4 = "ccsmcompset"
        self.__re4 = re.compile(self.__stringpattern4 + "$")

        self.__delimiter = "="

        self.__filename = "ccsm_definitions.txt"

        self.__ccsmmachine = ""
        self.__ccsmres = ""
        self.__ccsmtest = ""
        self.__ccsmcompset = ""
        self.__ccsmcase = ""

        #Read all the lines of the file.
        fileobj = open(self.__filename,'r')
        filerecords = fileobj.readlines()
        fileobj.close()

        #Parse for ccsm machine.
        for record1 in  filerecords:
            words = record1.split(self.__delimiter)
            words[0] = words[0].strip().lower()
            if self.__re1.match(words[0]):
                self.__ccsmmachine = words[1].strip()
                break

        #Parse for ccsm resolution.
        for record1 in  filerecords:
            words = record1.split(self.__delimiter)
            words[0] = words[0].strip().lower()
            if self.__re2.match(words[0]):
                self.__ccsmres = words[1].strip()
                break

        #Parse for ccsm test.
        for record1 in  filerecords:
            words = record1.split(self.__delimiter)
            words[0] = words[0].strip().lower()
            if self.__re3.match(words[0]):
                self.__ccsmtest = words[1].strip()
                break

        #Parse for ccsm compset.
        for record1 in  filerecords:
            words = record1.split(self.__delimiter)
            words[0] = words[0].strip().lower()
            if self.__re4.match(words[0]):
                self.__ccsmcompset = words[1].strip()
                break

        #Define the prefix for the case directory.
        self.__ccsmcase = self.__ccsmtest + "." + ccsm_utility.shortname[self.__ccsmres] + "." + self.__ccsmcompset + "." + self.__ccsmmachine

    def get_machine(self):
        return self.__ccsmmachine

    def  get_resolution(self):
        return self.__ccsmres

    def get_test(self):
        return self.__ccsmtest
    
    def get_compset(self):
        return self.__ccsmcompset

    def get_case(self):
        return self.__ccsmcase

    def get_case_location(self,testroot):
        case_dir = self.__ccsmcase + ".[0-9][0-9][0-9][0-9][0-9][0-9]"
        case_dir = os.path.join(testroot,case_dir)

        dirs = glob.glob(case_dir)

        path0 = dirs[0]
        basename = os.path.basename(path0)
        testscript = basename + ".test"
        testscript = os.path.join(path0,testscript)

        return (dirs[0],testscript)
