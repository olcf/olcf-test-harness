#! /usr/bin/env python3


import os
import socket
import string
import re
import time
import datetime

from libraries import aprun_3



class base_computer:

    MX_PEAK_FLOPS_PER_CPU = None


    list_of_computers = ["Chester","Titan"]
    days_of_week = { 1: "Mon", 
                     2: "Tue",
                     3: "Wed",
                     4: "Thu",
                     5: "Fri",
                     6: "Sat",
                     7: "Sun",
                  }
    months_of_year = { 1: "Jan",
                       2: "Feb",
                       3: "Mar",
                       4: "Apr",
                       5: "May",
                       6: "Jun",
                       7: "Jul",
                       8: "Aug",
                       9: "Sep",
                      10: "Oct",
                      11: "Nov",
                      12: "Dec",
                     }

    days_of_month = { 1 : "01",
                      2 : "02",
                      3 : "03",
                      4 : "04",
                      5 : "05",
                      6 : "06",
                      7 : "07",
                      8 : "08",
                      9 : "09",
                      10 :"10",
                      11 :"11",
                      12 :"12",
                      13 :"13",
                      14 :"14",
                      15 :"15",
                      16 :"16",
                      17 :"17",
                      18 :"18",
                      19 :"19",
                      20 :"20",
                      21 :"21",
                      22 :"22",
                      23 :"23",
                      24 :"24",
                      25 :"25",
                      26 :"26",
                      27 :"27",
                      28 :"28",
                      29 :"29",
                      30 :"30",
                      31 :"31",
                    }

    def __init__(self):
       self.name = None
       self.hasheventrecords = {}

    def get_event_records(self,startdate,enddate):
        oneday = datetime.timedelta(days=1)

        self.new_start_date = datetime.datetime(startdate.year,startdate.month,startdate.day)
        self.new_end_date = datetime.datetime(enddate.year,enddate.month,enddate.day)

        nextday = self.new_start_date
        tmpeventrecords = {}
        while nextday <= self.new_end_date:
            event_file_record = "/ccs/sys/adm/MOAB/titan/" + str(nextday.year) + "/" + str(titan_computer.days_of_month[nextday.month]) + "/" + str(titan_computer.days_of_month[nextday.day])
            if os.path.exists(event_file_record):

                fileobj = open(event_file_record,"r")
                self.hasheventrecords[nextday.isoformat("T")] = fileobj.readlines()
                fileobj.close()

            nextday = nextday + oneday


    def in_time_range(self,pbsid,creationtime,startdate,enddate):
        
        oneday = datetime.timedelta(days=1)

        (creationtime1, creationtime2) = creationtime.split("T")
        (year,month,day) = creationtime1.split("-")
        (time1,time2) = creationtime2.split(".")
        (hour,min,sec) = time1.split(":")
        creationdate = datetime.datetime(int(year),int(month),int(day))

        if creationdate > enddate:
            return False
        nextday = creationdate
        
        while nextday <= self.new_end_date:
            if nextday.isoformat("T") in self.hasheventrecords:
                for tmpevent in self.hasheventrecords[nextday.isoformat("T")]:
                    words = tmpevent.split()
                    if (len(words) >= 3) and (words[3] == pbsid) and (words[4] == "JOBEND"):
                        return True
            nextday = nextday + oneday


        return False

    def set_name(self,name):
        self.name = name

    def get_name(self):
        return self.name


    def end_time_of_job(self, pbsid,creationtime,startdate,enddate):
        return False

class chester_computer(base_computer):
    MX_PEAK_FLOPS_PER_CPU = 9.2
    MOAB_LOG_FILE_PATH = "/moab/stats"
    def __init__(self,hostname):
        base_computer.__init__(self)
        self.set_name(hostname)

    def get_max_flops_per_cpu(self):
        return chester_computer.MX_PEAK_FLOPS_PER_CPU

class titan_computer(base_computer):
    MX_PEAK_FLOPS_PER_CPU = 9.2
    MOAB_LOG_FILE_PATH = "/moab/stats"
    def __init__(self,hostname):
        base_computer.__init__(self)
        self.set_name(hostname)

    def get_max_flops_per_cpu(self):
        return titan_computer.MX_PEAK_FLOPS_PER_CPU


def create_computer():
    hostname = socket.getfqdn()
    chester_regep = re.compile("^Chester",re.I)
    titan_regep = re.compile("^Titan",re.I)
    
    #--Are we chester?
    if chester_regep.match(hostname):
        return chester_computer(hostname)
    #--Are we on Titan? 
    elif titan_regep.match(hostname):
        return titan_computer(hostname)
    else:
        string1 =  "Computer " + hostname + " not defined as a class."
        print(string1)




