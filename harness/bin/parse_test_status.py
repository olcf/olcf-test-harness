#!/usr/bin/env python3

# NCCS Test Harness Package Imports
from libraries.layout_of_apps_directory import apptest_layout


def main():
    string1 = "--------------------"

    filename=apptest_layout.test_pass_failed_status_filename
    file_obj = open(filename,"r")
    filerecords = file_obj.readlines()

    ip = -1
    total_test = 0
    total_passed = 0
    total_failed = 0
    total_inconclusive = 0
    test_with_no_passes = []
    for tmprecord in filerecords:
       ip = ip + 1
       if tmprecord.find(string1) != -1 :
          #print filerecords[ip+4],
          tmprecord1 = filerecords[ip+4].strip()
          words = tmprecord1.split()
          total_test = total_test + int(words[0])
          total_passed = total_passed + int(words[1])
          total_failed = total_failed + int(words[2])
          total_inconclusive = total_inconclusive + int(words[3])
          if int(words[1]) == 0:
             test_with_no_passes.append(filerecords[ip+2].strip())


    print ("Total tests: ",total_test)
    print ("Total passed: ",total_passed)
    print ("Total failed: ",total_failed)
    print ("Total inconclusive : ", total_inconclusive)
    print ("Pass percentage :", float(total_passed)/float(total_test))
    print
    print
    print
 
    print ("The following tests have no sucesses:")
    for test in test_with_no_passes:
       print (test)   

if __name__ == "__main__":
    main()
