#! /usr/bin/env python

import os
from libraries import apptest

class scalers:

    def __init__(self,
                 name_of_application=None,
                 name_of_subtest=None,
                 unique_id = None,
                 name_of_metric=None,
                 metric_units=None,
                 metric_start_time=None,
                 metric_end_time=None,
                 metric_value=None):

        self.__nameOfApplication = name_of_application
        self.__nameOfTest = name_of_subtest
        self.__uniqueID = unique_id
        self.__metricName = str(name_of_metric)
        self.__units = metric_units
        self.__startTime = metric_start_time
        self.__endTime = metric_end_time
        self.__value = metric_value

        starting_dir = os.environ["RGT_PATH_TO_SCRIPTS_DIR"]
        (headdir1,taildir1) = os.path.split(starting_dir)
        (headdir2,taildir2) = os.path.split(headdir1)
        (headdir3,taildir3) = os.path.split(headdir2)

        self.__appTest = apptest.subtest(name_of_application=self.__nameOfApplication,
                                         name_of_subtest=self.__nameOfTest,
                                         local_path_to_tests=headdir3)

        if self.__startTime == None:
            path = self.__appTest.get_local_path_to_start_binary_time(self.__uniqueID)
            if path:
                file_obj = open(path,"r")
                record = file_obj.readlines()
                file_obj.close()
                #print record
                
                tmp_record = record[0].strip()
                self.__startTime = tmp_record


        if self.__endTime == None:
            path = self.__appTest.get_local_path_to_end_binary_time(self.__uniqueID)
            if path:
                file_obj = open(path,"r")
                record = file_obj.readlines()
                file_obj.close()
                #print record
                
                tmp_record = record[0].strip()
                self.__endTime = tmp_record

        
    def recordMetric(self):
        dir1 = os.path.join(self.__appTest.get_local_path_to_performance_dir(),
                             self.__uniqueID)

        path1 = os.path.join(self.__appTest.get_local_path_to_performance_dir(),
                             self.__uniqueID,
                             self.__metricName)
       
        if os.path.exists(path1): 
            pass
            #print("Recording metric in : " + path1)
        else:
            if os.path.exists(dir1):
                pass
                #print("Recording metric in : " + path1)
            else:
                os.makedirs(dir1)

        file_obj = open(path1,"w")

        metric_data = "Metric_value = {0}\n".format(str(self.__value))

        metric_data = metric_data + \
                      "Unique_id = {0}\n".format(str(self.__uniqueID))

        if self.__startTime:
            metric_data = metric_data + \
                          "Start_time = {0}\n".format(self.__startTime)
        else:
            metric_data = metric_data + \
                          "Start_time = {0}\n".format("None")

        if self.__endTime:
            metric_data = metric_data + \
                          "Stop_time = {0}\n".format(self.__endTime)
        else:
            metric_data = metric_data + \
                          "Stop_time = {0}\n".format("None")

        if self.__units:
            metric_data = metric_data + \
                          "Metric_units = {0}\n".format(self.__units)
        else:
            metric_data = metric_data + \
                          "Metric_units = {0}\n".format("None")

        file_obj.write(metric_data)
        file_obj.close()

def getTargetMetric(path_to_correct_results,metric):
    correct_result = None
    filename = os.path.join(path_to_correct_results,metric)
    if os.path.isfile(filename):
        file_obj = open(filename,"r")
        records = file_obj.readlines()
        file_obj.close()

        for tmp_record in records:
            words = tmp_record.split()
            if words[0].strip() == "Metric_value":
                correct_result = words[2]

    return correct_result

            

