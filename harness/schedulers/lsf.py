import os
import subprocess

from .base import BaseScheduler, SchedulerJob


class LSF(BaseScheduler):
    """LSF scheduler class."""

    name: str = "LSF"
    submit_executable: str = "bsub"

    def _submit_as_stdin(self) -> bool:
        # default to stdin unless specified otherwise
        return (
            "RGT_LSF_SUBMIT_AS_STDIN" not in os.environ
            or str(os.environ["RGT_LSF_SUBMIT_AS_STDIN"]) != "0"
        )

    def submit_job(self, job: SchedulerJob) -> int:
        self._logger.log_info(
            f"Submitting job from LSF class using batchfilename {job.batch_script}"
        )

        submit_cmd = [self.submit_executable]

        if "RGT_SUBMIT_QUEUE" in os.environ:
            submit_cmd.extend(["-q", os.environ.get("RGT_SUBMIT_QUEUE")])
        elif "RGT_BATCH_QUEUE" in os.environ:
            submit_cmd.extend(["-q", os.environ.get("RGT_BATCH_QUEUE")])

        if "RGT_SUBMIT_ARGS" in os.environ:
            submit_cmd.extend(os.environ.get("RGT_SUBMIT_ARGS").split())

        if "RGT_SUBMIT_ACCT" in os.environ:
            submit_cmd.extend(["-P", os.environ.get("RGT_SUBMIT_ACCT")])
        elif "RGT_PROJECT_ID" in os.environ:
            submit_cmd.extend(["-P", os.environ.get("RGT_PROJECT_ID")])

        if not self._submit_as_stdin:
            submit_cmd.append(job.batch_script)

        self._logger.log_info(" ".join(submit_cmd))

        with open(self.submit_stdout_file, "w") as stdout, open(
            self.submit_stderr_file, "w"
        ) as stderr:
            if not self._submit_as_stdin:
                result = subprocess.run(
                    submit_cmd, stdout=stdout, stderr=stderr, check=False
                )
            else:
                with open(job.batch_script, "r") as batch_script:
                    result = subprocess.run(
                        submit_cmd,
                        stdout=stdout,
                        stderr=stderr,
                        stdin=batch_script,
                        check=False,
                    )

        with open(self.submit_stdout_file, "r") as submit_stdout:
            records = submit_stdout.readlines()

        if result.returncode == 0:
            job.id = self.job_id_regex.search(records[0]).group(0)
            self._logger.print(f"LSF JobID = {job.id}")
        else:
            with open(self.submit_stderr_file, "w") as submit_stderr:
                self._logger.log_critical(submit_stderr.read())

        return result.returncode
