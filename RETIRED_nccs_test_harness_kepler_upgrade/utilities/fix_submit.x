#! /usr/bin/env python

import shutil
import os
import copy
import popen2
import re

class submit_file():
    def __init__(self,filename):
        self.__template_file_name = filename

        dirpath = os.path.dirname(filename)
        self.__copy_template_file_name = os.path.join(dirpath,'submit_executable.copy_do_not_erase.x')
        self.__finalfilename = os.path.join(dirpath,'submit_executable.x.final')
        self.__finalfile = []

        #The qsub command to fix.
        self.__qsub_regexp = re.compile('qsub -V')
        self.__qsub_replacement = 'qsub'
        self.__replacement_q_comand_line = 'qcommand = "qsub -V " + batchfilename'

        #The hash to fix in submit.
        self.__hash_regexp = re.compile('__pbsaccountid__')
        self.__hash_regexp_1 = re.compile('pbsaccountid')
        self.__hash_replacement1 = 'rgtenvironmentalfile'
        self.__hash_replacement2 = 'nccstestharnessmodule'

        #The definitions to modify.
        self.__pbsaccountdefline_regexp  = re.compile('(\s+)pbsaccountid\s*=')
        self.__lines_to_add_1 = 'rgtenvironmentalfile = os.environ["RGT_ENVIRONMENTAL_FILE"]'
        self.__lines_to_add_2 = 'nccstestharnessmodule = os.environ["RGT_NCCS_TEST_HARNESS_MODULE"]' 

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

        
    def dump(self):
        file_obj = open (self.__template_file_name,'w')
        for record in self.__finalfile:
           file_obj.write(record)
        file_obj.close()

    def chmod(self):
       cmmd = "chmod +x " + self.__template_file_name
       os.system(cmmd)

    def fix_q_command(self):
        ip = -1
        for tmp_record in self.__finalfile:

            #We are on the ip'th record
            ip = ip + 1

            self.__finalfile[ip] = self.__qsub_regexp.sub(self.__qsub_replacement,tmp_record)
            if self.__qsub_regexp.match(tmp_record): 
                pass

    def fix_definitions(self):
        ip = -1
        for tmp_record in self.__finalfile:

            #We are on the ip'th record
            ip = ip + 1

            m1 = self.__pbsaccountdefline_regexp.match(tmp_record)
            if m1:
               l1 = m1.group(1) + self.__lines_to_add_1
               l2 = m1.group(1) + self.__lines_to_add_2
               tmp_record += l1 + '\n'
               tmp_record += l2 + '\n'
               self.__finalfile[ip] = tmp_record

    def fix_hash(self):
        ip = -1
        for tmp_record in self.__finalfile:

            #We are on the ip'th record
            ip = ip + 1

            if self.__hash_regexp.search(tmp_record): 
                self.__finalfile[ip] += self.__hash_regexp_1.sub(self.__hash_replacement1,tmp_record)
                self.__finalfile[ip] += self.__hash_regexp_1.sub(self.__hash_replacement2,tmp_record)

def get_submit_files():
    cmmd = 'find . -name submit_executable.x'
    find_cmmd = popen2.Popen3(cmmd)
    submit_files = find_cmmd.fromchild.readlines()
    ip = -1
    for file in submit_files:
        ip = ip + 1
        submit_files[ip] = file.strip()
    return submit_files



if __name__ == '__main__':

    submitfiles = get_submit_files()

    for tmpfile in submitfiles:
        f1 = submit_file(tmpfile)
       
        f1.fix_q_command() 

        f1.fix_definitions()

        f1.fix_hash()

        f1.dump()

        f1.chmod()
        
    
