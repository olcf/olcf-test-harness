import sys
import shutil
import os
import subprocess
import contextlib
import io
import tempfile

# NCCS Tesst Harness packages

class SVNRepository:
    """ This class is encapsulates the behavoir of a svn repository.

    """

    def __init__(self,
                 location_of_repository=None,
                 internal_repo_path_to_applications=None):
        self.__binaryName = "svn"
        self.__locationOfRepository = location_of_repository
        self.__internalPathToApplications = internal_repo_path_to_applications
        self.__checkedOutDirectories = []

        return

    def getLocationOfRepository(self):
        return self.__locationOfRepository

    def getLocationOfFile(self,
                          file):
        path_to_file = os.path.join(self.__locationOfRepository,
                                    self.__internalPathToApplications,
                                    file)
        return path_to_file

    def doSparseCheckout(self,
                         stdout_file_handle,
                         stderr_file_handle,
                         path_to_repository,
                         root_path_to_checkout_directory,
                         directory_to_checkout):
        """ Performs a sparse checkout of directory from the repository.

            :param stdout_file_handle: A file object to write standard out
            :type stdout_file_handle: A file object

            :param stderr_file_handle: A file object to write standard error
            :type stderr_file_handle: A file object

            :param path_to_repository: The url to the repository.
            :type path_to_repository: string

            :param root_path_to_checkout_directory: The fully qualified path the the to level of the sparse checkout directory.
            :type root_path_to_checkout_directory: string

            :param directory_to_checkout: A dictionary of directories or files to sparsely checkout.
            :type directories: a dictionary of strings of directory or file names.

            :returns: a tuple (message,exit_status) 
            :rtype:  message is a string, exit_status is an integer
        """
        message = ""
        exit_status = 0

        # Check if file handles are open
        if stdout_file_handle.closed:
            message +=  "Error! In sparse checkout the stdout file handle is closed"
            exit_status = 1
            return (message,exit_status)

        if stderr_file_handle.closed:
            message +=  "Error! In sparse checkout the stderr file handle is closed"
            exit_status = 1
            return (message,exit_status)

        # Define the svn options for a sparse checkout.
        svn_options = 'checkout -N'
       
        # Define the full qualified path the checkout location of the folder.
        tail_dir = os.path.basename(directory_to_checkout['application'])
        path_to_local_dir = os.path.join(root_path_to_checkout_directory,tail_dir)

        # Form the sparse checkout command for the application
        if not os.path.exists(path_to_local_dir):
            self.__checkedOutDirectories += [path_to_local_dir]
            sparse_checkout_command = "{my_bin} {my_options} {my_svn_path} {my_local_path}".format(
                                                my_bin = self.__binaryName, 
                                                my_options = svn_options, 
                                                my_svn_path = directory_to_checkout['application'],
                                                my_local_path = path_to_local_dir)

            exit_status = subprocess.call(sparse_checkout_command,
                                          shell=True,
                                          stdout=stdout_file_handle,
                                          stderr=stderr_file_handle)

            if exit_status > 0:
                message += "Sparse checkout of command failed: " + sparse_checkout_command
                return (message,exit_status)


        # Form the update command for the source
        application_dir = os.path.basename(directory_to_checkout['application'])
        tail_dir = os.path.basename(directory_to_checkout['source'])
        path_to_local_dir = os.path.join(root_path_to_checkout_directory,application_dir,tail_dir)
        
        self.__checkedOutDirectories += [path_to_local_dir]
        svn_options = 'update'
        svn_update_command = "{my_bin} {my_options} {my_local_path}".format(
                                            my_bin = self.__binaryName, 
                                            my_options = svn_options, 
                                            my_local_path = path_to_local_dir)
        
        exit_status = subprocess.call(svn_update_command,
                                      shell=True,
                                      stdout=stdout_file_handle,
                                      stderr=stderr_file_handle)

        if exit_status > 0:
            message += "svn update command failed: " + sparse_checkout_command
            return (message,exit_status)

        # Form the update command for the test.
        application_dir = os.path.basename(directory_to_checkout['application'])
        for a_test in directory_to_checkout['test']:
            tail_dir = os.path.basename(a_test)
            path_to_local_dir = os.path.join(root_path_to_checkout_directory,application_dir,tail_dir)
            self.__checkedOutDirectories += [path_to_local_dir]
            svn_options = 'update'
            svn_update_command = "{my_bin} {my_options} {my_local_path}".format(
                                                my_bin = self.__binaryName, 
                                                my_options = svn_options, 
                                                my_local_path = path_to_local_dir)
            
            exit_status = subprocess.call(svn_update_command,
                                          shell=True,
                                          stdout=stdout_file_handle,
                                          stderr=stderr_file_handle)

            if exit_status > 0:
                message += "svn update command failed: " + sparse_checkout_command
                return (message,exit_status)

        return (message,exit_status)

    def verifySparseCheckout(self):
        """ Verifies that the directories exist for a sparse checkout.

            :returns: a tuple (message,exit_status) 
            :rtype:  message is a string, exit_status is an integer
        """

        test_result = True
        message = ""
        for dirpath in self.__checkedOutDirectories:
            if not os.path.exists(dirpath):
                test_result = False
                message += "Directory/file {0} did not checkout.".format(dirpath)
        return (message, test_result)


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
