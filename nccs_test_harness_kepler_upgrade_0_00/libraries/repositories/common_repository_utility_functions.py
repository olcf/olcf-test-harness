import sys
import shutil
import os
import subprocess
import contextlib
import io
import tempfile

# NCCS Tesst Harness packages

def run_as_subprocess_command(cmd):
    """ Runs the command in the string cmd by subprocess.

            :param cmd: A string containing the command to run
            :type cmd: string
    """
    # Run the command and write the command's 
    # stderr and stdout results to 
    # unique temp files. The stdout tempfile has only one record which 
    # is searched for true or false. If true is found then
    # sparse checkout is enabled, otherwise sparse checkouts are
    # not enabled and we exit program.
    exit_status = 0
    with tempfile.NamedTemporaryFile("w",delete=False) as tmpfile_stdout:
        with tempfile.NamedTemporaryFile("w",delete=False) as tmpfile_stderr:
            exit_status = None
            message = None
            try:
                exit_status = subprocess.check_call(cmd,
                                                    shell=True,
                                                    stdout=tmpfile_stdout,
                                                    stderr=tmpfile_stderr)
            except subprocess.CalledProcessError as exc :
                exit_status = 1
                message = "Error in subprocess command: " + exc.cmd
            except:
                exit_status = 1
                message = "Unexpected error in command! " + cmd
    
            # Close the file objects of the temporary files.
            tmpfile_stdout_path = tmpfile_stdout.name
            tmpfile_stderr_path = tmpfile_stderr.name
            tmpfile_stdout.close()
            tmpfile_stderr.close()
    
            # Remove the temporary files if the subprocess fails.
            if  exit_status > 0:
                os.remove(tmpfile_stdout_path) 
                os.remove(tmpfile_stderr_path) 
                sys.exit(message)
    
            # Remove the temporary files before we return.
            os.remove(tmpfile_stdout_path) 
            os.remove(tmpfile_stderr_path) 
    return

def run_as_subprocess_command_return_stdout_stderr(cmd):
    """ Runs the command in the string cmd by subprocess.

            :param cmd: A string containing the command to run
            :type cmd: string
    """
    # Run the command and write the command's 
    # stderr and stdout results to 
    # unique temp files. The stdout tempfile has only one record which 
    # is searched for true or false. If true is found then
    # sparse checkout is enabled, otherwise sparse checkouts are
    # not enabled and we exit program.
    exit_status = 0
    with tempfile.NamedTemporaryFile("w",delete=False) as tmpfile_stdout:
        with tempfile.NamedTemporaryFile("w",delete=False) as tmpfile_stderr:
            exit_status = None
            message = None
            try:
                initial_dir = os.getcwd()
                exit_status = subprocess.check_call(cmd,
                                                    shell=True,
                                                    stdout=tmpfile_stdout,
                                                    stderr=tmpfile_stderr)
            except subprocess.CalledProcessError as exc :
                exit_status = 1
                message = "Error in subprocess command: " + exc.cmd
            except:
                exit_status = 1
                message = "Unexpected error in command! " + cmd
    
            # Close the file objects of the temporary files.
            tmpfile_stdout_path = tmpfile_stdout.name
            tmpfile_stderr_path = tmpfile_stderr.name
            tmpfile_stdout.close()
            tmpfile_stderr.close()
    
            # Copy the contents of tmpfile_stdout_path and tmpfile_stderr_path
            # to stdout and stderr.
            stdout_file_obj = open(tmpfile_stdout_path,"r" )
            stderr_file_obj = open(tmpfile_stderr_path,"r" )

            stdout = stdout_file_obj.readlines()
            stderr = stderr_file_obj.readlines()

            stdout_file_obj.close()
            stderr_file_obj.close()
            
            # Remove the temporary files before we return.
            os.remove(tmpfile_stdout_path) 
            os.remove(tmpfile_stderr_path) 

    return (stdout,stderr)

def get_type_of_repository():
    return os.getenv('RGT_TYPE_OF_REPOSITORY')

def get_location_of_repository():
    return (os.getenv("RGT_PATH_TO_REPS"),os.getenv("RGT_PATH_TO_REPS_INTERNAL"),os.getenv("MY_APP_REPO_BRANCH"))
