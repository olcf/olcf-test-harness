#! /usr/bin/python

# Python package imports
import re

# NCCS Test Harness Package Imports
from libraries.layout_of_apps_directory import apptest_layout

class teststatusfile:
    def __init__(self,test_status_file):
        self.__tsf = test_status_file
        self.__totaltests = 0
        self.__totalpassed = 0
        self.__totalfailed = 0
        self.__totalincinclusive = 0
        self.__re_theader = re.compile('^--------------------')
        self.__re_bheader = re.compile('^====================')
        
        #--Read the lines of the test_status file.
        tfileobj = open(self.__tsf,'r')
        self.__alllines = tfileobj.readlines()
        tfileobj.close()

        self.__tests = []
        
        ip = -1
        found_theader = -1
        found_bheader = -1
        for line in self.__alllines:
            ip = ip + 1

            #--Check if top header is found.
            if self.__re_theader.search(line):
                found_theader = ip
                

            #--Check if bottom header is found.
            if self.__re_bheader.search(line):
                found_bheader = ip


            #Test uf flags for resetting found_theader and found_bheader are to be reset.
            if (found_theader >=0) and (found_bheader >=0):
                #Get the line that containes the status of the test.
                kp = found_theader + 4

                #Split tthat line for the stats.
                words =  self.__alllines[kp].split() 


                self.__totaltests = self.__totaltests + int(words[0])
                self.__totalpassed = self.__totalpassed + int(words[1])
                self.__totalfailed = self.__totalfailed + int(words[2])
                self.__totalincinclusive = self.__totalincinclusive + int(words[3])

                found_theader = -1
                found_bheader = -1
        s1 = "%20s %20s %20s %20s\n" % ("Total tests","Test passed", "Test failed", "Test inconclusive")
        s2 = "%20s %20s %20s %20s\n" % (str(self.__totaltests),
                                        str(self.__totalpassed),
                                        str(self.__totalfailed),
                                        str(self.__totalincinclusive)
                                       )
        s3 = "%20s %20s %20s %20s\n" % ('(percentages)',
                                        str(float(self.__totalpassed)/float(self.__totaltests)),
                                        str(float(self.__totalfailed)/float(self.__totaltests)),
                                        str(float(self.__totalincinclusive)/float(self.__totaltests))
                                       )
        print (s1,s2,s3)

def main():
    filename=apptest_layout.test_pass_failed_status_filename
    t1 = teststatusfile(filename)   


if __name__ == "__main__" :
    main()
