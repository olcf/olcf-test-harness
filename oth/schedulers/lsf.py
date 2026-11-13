import subprocess

from .base import BaseScheduler, SchedulerJob


class LSF(BaseScheduler):
    """LSF scheduler class."""

    name: str = "LSF"
    submit_executable: str = "bsub"

    def submit_job(self, job: SchedulerJob) -> int:

        from oth.config import othctl_runtime_config

        self._logger.log_info(
            f"Submitting job from LSF class using batchfilename {job.batch_script}"
        )

        submit_cmd = [self.submit_executable]

        if othctl_runtime_config.submit_queue:
            submit_cmd.extend(["-q", othctl_runtime_config.submit_queue])
        elif othctl_runtime_config.batch_queue:
            submit_cmd.extend(["-q", othctl_runtime_config.batch_queue])

        if othctl_runtime_config.submit_args:
            submit_cmd.extend(othctl_runtime_config.submit_args.split())

        if othctl_runtime_config.submit_acct:
            submit_cmd.extend(["-P", othctl_runtime_config.submit_acct])
        elif othctl_runtime_config.project_id:
            submit_cmd.extend(["-P", othctl_runtime_config.project_id])

        if othctl_runtime_config.lsf_submit_as_stdin == "0":
            submit_cmd.append(job.batch_script)

        self._logger.log_info(" ".join(submit_cmd))

        with open(self.submit_stdout_file, "w") as stdout, open(
            self.submit_stderr_file, "w"
        ) as stderr:
            if othctl_runtime_config.lsf_submit_as_stdin == "0":
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
            job_id_search = self.job_id_regex.search(records[0])
            if job_id_search:
                job.id = job_id_search.group(0)
                self._logger.print(f"LSF JobID = {job.id}")
        else:
            with open(self.submit_stderr_file, "r") as submit_stderr:
                self._logger.log_critical(submit_stderr.read())

        return result.returncode
