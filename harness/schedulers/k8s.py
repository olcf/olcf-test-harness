import subprocess as sp
from typing import List


import yaml
import json

from .base import BaseScheduler, SchedulerJob


class K8S(BaseScheduler):
    """K8S scheduler class"""

    name: str = "K8S"
    submit_executable: str = "kubectl"

    def submit_job(self, job: SchedulerJob) -> int:
        self._logger.log_info(
            f"Submitting job from K8S class using batchfilename {job.batch_script}"
        )

        submit_cmd: List[str] = [
            self.submit_executable,
            "apply",
            "-f",
            job.batch_script,
            "-o",
            "json",
        ]

        with open(self.submit_stdout_file, "w") as stdout, open(
            self.submit_stderr_file, "w"
        ) as stderr:
            result = sp.run(submit_cmd, stdout=stdout, stderr=stderr, check=False)

        if result.returncode == 0:
            with open(job.batch_script, "r") as f:
                job_yaml = yaml.safe_load(f)
                job.name = job_yaml["metadata"]["name"]
                self._logger.print(f"K8S JobName = {job.name}")
            with open(self.submit_stdout_file, "r") as f_stdout:
                cluster_response = json.load(f_stdout)
                job.id = cluster_response["metadata"]["uid"]
                self._logger.print(f"K8S JobID = {job.id}")
        else:
            with open(self.submit_stderr_file, "r") as submit_stderr:
                self._logger.log_critical(submit_stderr.read())

        return result.returncode
