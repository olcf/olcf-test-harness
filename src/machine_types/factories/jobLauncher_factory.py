from machine_types.job_launchers.aprun import Aprun
from machine_types.job_launchers.poe import Poe

class JobLauncherFactory:

    @staticmethod
    def create_jobLauncher(jobLauncher_type):
        print("Creating jobLauncher")

        tmp_jobLauncher = None
        if jobLauncher_type == "aprun":
            tmp_jobLauncher = Aprun()
        elif jobLauncher_type == "poe":
            tmp_jobLauncher = Poe()
        else:
            print("Job launcher not supported. Good bye!")

        return tmp_jobLauncher


    def __init__(self):
        pass

