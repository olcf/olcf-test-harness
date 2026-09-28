import os
import subprocess

from .base import BaseScheduler, SchedulerJob


class PBS(BaseScheduler):
    """PBS scheduler class."""

    name: str = "PBS"
    submit_executable: str = "qsub"

    def submit_job(self, job: SchedulerJob) -> int:
        self._logger.log_info(
            f"Submitting job from PBS class using batchfilename {job.batch_script}"
        )

        submit_cmd = [self.submit_executable]

        if "RGT_SUBMIT_QUEUE" in os.environ:
            submit_cmd.extend(["-q", os.environ.get("RGT_SUBMIT_QUEUE")])
        elif "RGT_BATCH_QUEUE" in os.environ:
            submit_cmd.extend(["-q", os.environ.get("RGT_BATCH_QUEUE")])

        if "RGT_SUBMIT_ARGS" in os.environ:
            submit_cmd.extend(os.environ.get("RGT_SUBMIT_ARGS").split())

        if "RGT_SUBMIT_ACCT" in os.environ:
            submit_cmd.extend(["-A", os.environ.get("RGT_SUBMIT_ACCT")])
        elif "RGT_PROJECT_ID" in os.environ:
            submit_cmd.extend(["-A", os.environ.get("RGT_PROJECT_ID")])

        submit_cmd.append(job.batch_script)

        self._logger.log_info(" ".join(submit_cmd))

        with (
            open(self.submit_stdout_file, "w") as stdout,
            open(self.submit_stderr_file, "w") as stderr,
        ):
            result = subprocess.run(submit_cmd, stdout=stdout, stderr=stderr)

        with open(self.submit_stdout_file, "r") as submit_stdout:
            records = submit_stdout.readlines()

        if result.returncode == 0:
            job.id = self.job_id_regex.search(records[0]).group(0)
            self._logger.print(f"PBS JobID = {job.id}")
        else:
            with open(self.submit_stderr_file, "w") as submit_stderr:
                self._logger.log_critical(submit_stderr.read())

        return result.returncode
