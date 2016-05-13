#!/usr/bin/env python
#
# Author: Veronica G. Vergara L.
#
#

from machine_types.machines.base_machine import BaseMachine

class IBMpower8(BaseMachine):
    
    def __init__(self,name='IBM Power8',scheduler=None,jobLauncher=None,
                 numNodes=0,numSocketsPerNode=0,numCoresPerSocket=0):
        BaseMachine.__init__(self,name,scheduler,jobLauncher,numNodes,
                             numSocketsPerNode,numCoresPerSocket)

if __name__ == "__main__":
    print('This is the IBM Power8 class')
