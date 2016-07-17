#!/usr/bin/env python
#
# Author: Veronica G. Vergara L.
#
#

from .base_machine import BaseMachine
import os

class IBMpower8(BaseMachine):
    
    def __init__(self,name='IBM Power8',scheduler=None,jobLauncher=None,
                 numNodes=0,numSocketsPerNode=0,numCoresPerSocket=0,rgt_test_input_file="rgt_test_input.txt"):
        BaseMachine.__init__(self,name,scheduler,jobLauncher,numNodes,
                             numSocketsPerNode,numCoresPerSocket,rgt_test_input_file)
        self.__rgt_test_input = None

    def read_rgt_test_input(self):
        if os.path.isfile(self.get_rgt_input_file_name()):
            print("Reading input file from Power8")
        else:
            print("No input found. Provide your own scripts")

    def make_batch_script(self):
        print("Making batch script for Power8")
        self.read_rgt_test_input()
        return

    def submit_batch_script(self):
        print("Submitting batch script for Power8")
        return

if __name__ == "__main__":
    print('This is the IBM Power8 class')
