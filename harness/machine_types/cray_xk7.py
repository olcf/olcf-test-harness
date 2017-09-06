#!/usr/bin/env python
#
# Author: Veronica G. Vergara L.
#
#

from .base_machine import BaseMachine

class CrayXK7(BaseMachine):

    def __init__(self,name='Cray XK7',scheduler=None,jobLauncher=None,
                 numNodes=0,numSocketsPerNode=0,numCoresPerSocket=0):
        BaseMachine.__init__(self,name,scheduler,jobLauncher,numNodes,
                             numSocketsPerNode,numCoresPerSocket)

if __name__ == '__main__':
    print('This is the Cray XK7 class')
