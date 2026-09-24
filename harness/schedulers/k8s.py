#!/usr/bin/env python
#
# Author: Elijah A. MacCarthy
#
#

import os
import shlex
import subprocess
import re
import yaml

from .base_scheduler import BaseScheduler

class K8S(BaseScheduler):

    """ K8S class represents an K8S scheduler. """

    def __init__(self, logger, use_jinja2=False):
        self.__name = 'oc'
        self.__submitCmd = 'oc apply -f '
        self.__statusCmd = 'oc get jobs'
        self.__deleteCmd = 'oc delete job'
        self.__walltimeOpt = None
        self.__numTasksOpt = None
        self.__jobNameOpt = None
        self.__templateFile = 'k8s.template.x' if not use_jinja2 else 'k8s.template.j2'
        self.__logger = logger
        BaseScheduler.__init__(self, self.__name,
                               self.__submitCmd, self.__statusCmd, self.__deleteCmd,
                               self.__walltimeOpt, self.__numTasksOpt, self.__jobNameOpt,
                               self.__templateFile)

    def submit_job(self, batchfilename):
        self.__logger.doInfoLogging(f"Submitting job from K8S class using batchfilename {batchfilename}")

        qcommand = f"{self.__submitCmd} {batchfilename}"

        self.__logger.doInfoLogging(qcommand)

        args = shlex.split(qcommand)

        result = subprocess.run(
            args,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True
        )

        if result.returncode == 0:

            self.__logger.doInfoLogging(result.stdout)

            #
            # Extract job name from YAML
            #
            with open(batchfilename, "r") as f:
                job_yaml = yaml.safe_load(f)

            job_name = job_yaml["metadata"]["name"]

            self.set_job_id(job_name)

            self.__logger.doInfoLogging(
                f"K8S job name = {self.get_job_id()}"
            )

        else:
            self.__logger.doCriticalLogging(result.stderr)

        return result.returncode

    def set_job_id_from_environ(self):
        self.__logger.doInfoLogging("Setting job id from environment in k8s class")
        jobvar = 'HOSTNAME'
        if jobvar in os.environ:
            self.set_job_id(os.environ[jobvar])
        else:
            self.__logger.doErrorLogging(f'{jobvar} not set in environment!')


if __name__ == '__main__':
    print('This is the k8s scheduler class')
