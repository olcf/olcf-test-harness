import sys
import shutil
import os
import subprocess
import contextlib
import io
import tempfile

# NCCS Tesst Harness packages

format_subprocess_command  = "\n"
format_subprocess_command += "===========================\n"
format_subprocess_command += "Error in subprocess command: {command}\n"
format_subprocess_command += "===========================\n"
format_subprocess_command += "Standard out:\n"
format_subprocess_command += "{standard_output}"
format_subprocess_command += "\n\n"
format_subprocess_command += "Standard error:\n"
format_subprocess_command += "{standard_error}"
format_subprocess_command += "\n\n"
format_subprocess_command += "===========================\n\n"


def run_as_subprocess_command(cmd,
                              command_execution_directory=None):
    """ Runs the command in the string cmd by subprocess.

            :param cmd: A string containing the command to run
            :type cmd: string

            :param command_execution_directory: The directory where the command is executed.
            :type command_execution_directory: string
    """

    exit_status = 0

    if command_execution_directory:
        my_command = "cd {dir}; {command}".format(dir=command_execution_directory,
                                                  command=cmd)
    else:
        my_command = cmd

    with tempfile.NamedTemporaryFile("w+b",delete=False) as tmpfile_stdout:
        with tempfile.NamedTemporaryFile("w+b",delete=False) as tmpfile_stderr:
            exit_status = None
            message = None
            try:
                exit_status = subprocess.check_call(my_command,
                                                    shell=True,
                                                    stdout=tmpfile_stdout,
                                                    stderr=tmpfile_stderr)
            except subprocess.CalledProcessError as exc :
                exit_status = 1

                # Read the standard out of the subprocess command.
                tmpfile_stdout.seek(0)
                stdout_message = tmpfile_stdout.read()

                # Read the standard error of the subprocess command.
                tmpfile_stderr.seek(0)
                stderr_message = tmpfile_stderr.read()

                message = format_subprocess_command.format(command=exc.cmd,
                                                           standard_output=stdout_message,
                                                           standard_error=stderr_message)
            except:
                exit_status = 1

                # Read the standard out of the subprocess command.
                tmpfile_stdout.seek(0)
                stdout_message = tmpfile_stdout.read()

                # Read the standard error of the subprocess command.
                tmpfile_stderr.seek(0)
                stderr_message = tmpfile_stderr.read()

                message = format_subprocess_command.format(command=my_command,
                                                           standard_output=stdout_message,
                                                           standard_error=stderr_message)

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
            else:
                # Remove the temporary files before we return.
                os.remove(tmpfile_stdout_path) 
                os.remove(tmpfile_stderr_path) 
    return

def run_as_subprocess_command_return_stdout_stderr(cmd,
                                                   command_execution_directory=None):
    """ Runs the command in the string cmd by subprocess.

            :param cmd: A string containing the command to run
            :type cmd: string

            :param command_execution_directory: The directory where the command is executed.
            :type command_execution_directory: string
    """

    exit_status = 0

    if command_execution_directory:
        my_command = "cd {dir}; {command}".format(dir=command_execution_directory,
                                                  command=cmd)
    else:
        my_command = cmd

    with tempfile.NamedTemporaryFile("w",delete=False) as tmpfile_stdout:
        with tempfile.NamedTemporaryFile("w",delete=False) as tmpfile_stderr:
            exit_status = None
            message = None
            try:
                initial_dir = os.getcwd()
                exit_status = subprocess.check_call(my_command,
                                                    shell=True,
                                                    stdout=tmpfile_stdout,
                                                    stderr=tmpfile_stderr)
            except subprocess.CalledProcessError as exc :
                exit_status = 1
                message = "Error in subprocess command: " + exc.cmd
            except:
                exit_status = 1
                message = "Unexpected error in command! " + my_command
    
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

def run_as_subprocess_command_return_stdout_stderr_exitstatus(cmd,
                                                              command_execution_directory=None):
    """ Runs the command in the string cmd by subprocess.

            :param cmd: A string containing the command to run
            :type cmd: string

            :param command_execution_directory: The directory where the command is executed.
            :type command_execution_directory: string
    """

    exit_status = 0

    if command_execution_directory:
        my_command = "cd {dir}; {command}".format(dir=command_execution_directory,
                                                  command=cmd)
    else:
        my_command = cmd

    with tempfile.NamedTemporaryFile("w",delete=False) as tmpfile_stdout:
        with tempfile.NamedTemporaryFile("w",delete=False) as tmpfile_stderr:
            exit_status = None
            message = None
            try:
                initial_dir = os.getcwd()
                exit_status = subprocess.check_call(my_command,
                                                    shell=True,
                                                    stdout=tmpfile_stdout,
                                                    stderr=tmpfile_stderr)
            except subprocess.CalledProcessError as exc :
                exit_status = 1
                message = "Error in subprocess command: " + exc.cmd
            except:
                exit_status = 1
                message = "Unexpected error in command! " + my_command
    
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

    return (stdout,stderr,exit_status)

def run_as_subprocess_command_return_exitstatus(cmd,
                                                command_execution_directory=None):
    """ Runs the command in the string cmd by subprocess.

            :param cmd: A string containing the command to run
            :type cmd: string

            :param command_execution_directory: The directory where the command is executed.
            :type command_execution_directory: string
    """
    exit_status = 0
    stdout = " Standard output piped to screen"
    stderr = " Standard error piped to screen"
    if command_execution_directory:
        my_command = "cd {dir}; {command}".format(dir=command_execution_directory,
                                                  command=cmd)
    else:
        my_command = cmd
        exit_status = None

    message = None

    try:
        initial_dir = os.getcwd()
        exit_status = subprocess.check_call(my_command,
                                            shell=True,
                                            stdout=None,
                                            stderr=None)
    except subprocess.CalledProcessError as exc :
        exit_status = 1
        message = "Error in subprocess command: " + exc.cmd
    except:
        exit_status = 1
        message = "Unexpected error in command! " + my_command
    
    return (stdout,stderr,exit_status)

