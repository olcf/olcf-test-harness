import sys
import shutil
import os
import subprocess
import contextlib
import io
import tempfile
from operator import contains

# NCCS Tesst Harness packages
from libraries.repositories.common_repository_utility_functions import run_as_subprocess_command
from libraries.repositories.abstract_repository import BaseRepository

class SVNRepository(BaseRepository):
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
                         root_path_to_checkout_directory,
                         directory_to_checkout):
        """ Performs a sparse checkout of directory from the repository.

            :param stdout_file_handle: A file object to write standard out
            :type stdout_file_handle: A file object

            :param stderr_file_handle: A file object to write standard error
            :type stderr_file_handle: A file object

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

        # Here we checkout the application.
        (message,exit_status) = \
        self.__doEmptyCheckoutOfApplication(directory_to_checkout,
                                            root_path_to_checkout_directory,
                                            stdout_file_handle,
                                            stderr_file_handle)

        # Here we update the source.
        (message,exit_status) = \
        self.__updateApplicationSource(directory_to_checkout,
                                       root_path_to_checkout_directory,
                                       stdout_file_handle,
                                       stderr_file_handle)

        # Here we update the tests.
        (message,exit_status) = \
        self.__updateApplicationTests(directory_to_checkout,
                                      root_path_to_checkout_directory,
                                      stdout_file_handle,
                                      stderr_file_handle)

        return (message,exit_status)

    def doSparseSourceCheckout(self,
                               application_name)
        """Does sparse checkout of source applications source directory"""
        message = ""
        exit_status = 0

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
                message += "Directory/file {0} did not checkout.\n".format(dirpath)
        return (message, test_result)


    def removeRepository(self):
        svn_url_prefix = "file://"
        tmp_words = self.__locationOfRepository.split(svn_url_prefix)
        shutil.rmtree(tmp_words[-1])
        return

    def __doEmptyCheckoutOfApplication(self,
                                       directory_to_checkout,
                                       root_path_to_checkout_directory,
                                       stdout_file_handle,
                                       stderr_file_handle):
        message = ""
        exit_status = 0

        # Define the svn options for a sparse checkout.
        svn_options = 'checkout -N'
       
        # Define the full qualified path the checkout location of the folder.
        tail_dir = os.path.basename(directory_to_checkout['application'])
        path_to_local_dir = os.path.join(root_path_to_checkout_directory,tail_dir)

        if not os.path.exists(path_to_local_dir):

            if not contains(self.__checkedOutDirectories,path_to_local_dir):
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
        return (message,exit_status)

    def __updateApplicationSource(self,
                                  directory_to_checkout,
                                  root_path_to_checkout_directory,
                                  stdout_file_handle,
                                  stderr_file_handle):
        message = ''
        exit_status = 0

        application_dir_head = os.path.basename(directory_to_checkout['application'])
        application_dir_tail = directory_to_checkout['application']
        my_repository_location = self.__locationOfRepository

        tmp_words = directory_to_checkout['source'].split(application_dir_tail)
        last_word = tmp_words[-1]
        path_to_local_dir = os.path.join(root_path_to_checkout_directory,application_dir_head,last_word[1:])

        if not contains(self.__checkedOutDirectories,path_to_local_dir):
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

    def __updateApplicationTests(self,
                                 directory_to_checkout,
                                 root_path_to_checkout_directory,
                                 stdout_file_handle,
                                 stderr_file_handle ):

        message = ''
        exit_status = 0

        # Form the update command for the test.
        application_dir_head = os.path.basename(directory_to_checkout['application'])
        application_dir_tail = directory_to_checkout['application']
        my_repository_location = self.__locationOfRepository

        svn_options = 'update'
        for a_test in directory_to_checkout['test']:
            tmp_words = a_test.split(application_dir_tail)
            last_word = tmp_words[-1]
            path_to_local_dir = os.path.join(root_path_to_checkout_directory,application_dir_head,last_word[1:])

            if not contains(self.__checkedOutDirectories,path_to_local_dir):
                self.__checkedOutDirectories += [path_to_local_dir]

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
