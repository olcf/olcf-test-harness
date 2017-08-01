#!/usr/bin/env python
#
# Author: Veronica G. Vergara L.
#
#

from aprun import Aprun
from poe import Poe
from jsrun import Jsrun

class JobLauncherFactory:

    @staticmethod
    def create_jobLauncher(jobLauncher_type):
        print("Creating jobLauncher")

        tmp_jobLauncher = None
        if jobLauncher_type == "aprun":
            tmp_jobLauncher = Aprun()
        elif jobLauncher_type == "poe":
            tmp_jobLauncher = Poe()
        elif jobLauncher_type == "jsrun":
            tmp_jobLauncher = Jsrun()
        else:
            print("Job launcher not supported. Good bye!")

        return tmp_jobLauncher


    def __init__(self):
        pass

