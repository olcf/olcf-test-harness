#! /usr/bin/env python3

import shutil
import os
import copy
import popen2
import re

class pbs_template():
    def __init__(self,filename):
        self.__template_file_name = filename

        dirpath = os.path.dirname(filename)
        self.__copy_template_file_name = os.path.join(dirpath,'pbs.template.x.copy_do_not_erase.x')
        self.__finalfilename = os.path.join(dirpath,'pbs.template.x.final')
        self.__finalfile = []

        #The first line and its replacement.
        self.__firstline = '#!/usr/bin/env bash'
        self.__firstline_regexp = re.compile('^#!\s+/usr/bin/env\s+bash')
        self.__replacement_of_firstline = '#!/bin/bash -l\n'


        #The environmental lines to replace.
        self.__accountlinewords = "#PBS -A __pbsaccountid__"
        self.__replacement_env_lines ='\n'
        self.__replacement_env_lines += '#-------------------------------------------\n'
        self.__replacement_env_lines += 'source __rgtenvironmentalfile__\n'
        self.__replacement_env_lines += 'module load __nccstestharnessmodule__\n'
        self.__replacement_env_lines += '#-------------------------------------------\n'

        #First make a copy of the original file.
        src_file = self.__template_file_name
        dst_file = self.__copy_template_file_name
        if (not os.path.exists(dst_file)):
            shutil.copy(src_file,dst_file)

        #Read the records of the file
        file_obj = open(dst_file,'r')
        tmpfile = file_obj.readlines()
        file_obj.close()

        self.__finalfile = tmpfile


    def fix_first_line(self):
        #Split the first line into words.
        firstlinewords = self.__firstline.split()

        #Make a deep copy of the records of the file
        tmpfile = copy.deepcopy(self.__finalfile)

        ip = -1
        for tmp_record in tmpfile:

            #We are on the ip'th record
            ip = ip + 1

            #Strip all leading and trailing whitespace form the record.
            tmp_record_1 = tmp_record.strip()
            temp_words_1 = tmp_record_1.split()

            if (self.__firstline_regexp.match(tmp_record)):
                tmpfile[ip] = self.__replacement_of_firstline
        
        self.__finalfile = copy.deepcopy(tmpfile)

    def add_environmental_lines(self):
        #Split the pbs account line into words.
        accountlinewords = self.__accountlinewords.split()

        #Make a deep copy of the records of the file
        tmpfile = copy.deepcopy(self.__finalfile)

        ip = -1
        for tmp_record in tmpfile:

            #We are on the ip'th record
            ip = ip + 1

            #Strip all leading and trailing whitespace form the record.
            tmp_record_1 = tmp_record.strip()
            temp_words_1 = tmp_record_1.split()

            if (len(temp_words_1) == 3) and (temp_words_1[0].find(accountlinewords[0]) >=  0 and (temp_words_1[1].find(accountlinewords[1]) >=  0) and (temp_words_1[2].find(accountlinewords[2]) >=  0)) :
                tmpfile[ip] = self.__accountlinewords +'\n' +  self.__replacement_env_lines
        
        self.__finalfile = copy.deepcopy(tmpfile)

        
    def dump(self):
        file_obj = open (self.__template_file_name,'w')
        for record in self.__finalfile:
           file_obj.write(record)
        file_obj.close()

def get_pbs_template_files():
    cmmd = 'find . -name pbs.template.x'
    find_cmmd = popen2.Popen3(cmmd)
    pbs_files = find_cmmd.fromchild.readlines()
    ip = -1
    for file in pbs_files:
        ip = ip + 1
        pbs_files[ip] = file.strip()
    return pbs_files


def get_submit_files():
    cmmd = 'find . -name submit_executable.x'
    find_cmmd = popen2.Popen3(cmmd)
    submit_files = find_cmmd.fromchild.readlines()
    ip = -1
    for file in pbs_files:
        ip = ip + 1
        submit_files[ip] = file.strip()
    return submit_files


if __name__ == '__main__':

    pbs_files = get_pbs_template_files()
    sunbit_files = get_submit_files()

    for tmpfile in pbs_files:
        f1 = pbs_template(tmpfile)
        
        f1.fix_first_line()

        f1.add_environmental_lines()

        f1.dump()
        
    
