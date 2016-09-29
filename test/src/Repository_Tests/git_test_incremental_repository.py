#! /usr/bin/env python3
""" Test class module verifies repositories encapsulation works.  """

import unittest
import os
import shutil

# NCCS Test Harness package imports
from libraries.repositories import RepositoryFactory
from libraries.repositories import get_type_of_repository
from libraries.repositories import types_of_repositories
from src.Repository_Tests import get_path_to_sample_directory
from src.Repository_Tests import get_path_to_application_directory
from src.Repository_Tests import create_application_directory
from src.Repository_Tests import creating_root_dir_repo

# Define the type of repository we are testing for these unit
# tests- git type. This variable is used to skip all tests that are not 
# of the same type.
this_repo_type = types_of_repositories["git"]

# The test condition for our skip decorator.
correct_repository_type = get_type_of_repository() == this_repo_type

# Our skip message
skip_message = \
    "We are running tests for a git repository, but our repository is of type {}".format(os.getenv('RGT_TYPE_OF_REPOSITORY') )

@unittest.skipUnless(correct_repository_type,skip_message)
class Test_Git_repositories(unittest.TestCase):
    """ Tests for repository functionality

        This class tests if the git repository class can
        do sparse checkout.

    """

    @classmethod
    def setUpClass(self):
        """ Set up to run basic repository tests. """
        # Define standard out and error file names for commands
        self.stdout_path = {'sparse_checkout' : os.path.join( os.path.abspath('.'), 'git_sparse_checkout.stdout.txt')}
        self.stderr_path = {'sparse_checkout' : os.path.join( os.path.abspath('.'), 'git_sparse_checkout.stderr.txt')}

        # Make a local git repository
        path_to_sample_directory = get_path_to_sample_directory()
        (path_to_test_repository,path_relative_path_to_apps_wrt_test_git_repository) = \
            get_path_local_repository_directory()

        self.repository = RepositoryFactory.createLocalGitRepoFromExistingDirectory(path_to_sample_directory,
                                                                                    path_to_test_repository,
                                                                                    path_relative_path_to_apps_wrt_test_git_repository)

        # Define the path to the repository.
        self.pathToRepository = get_path_to_test_repository()

        # Make the application directory - this directory will contain the sparse
        # checkout of the Application and test.
        self.pathToApplications = get_path_to_application_directory("git_sparse_checkout_applications")
        create_application_directory(self)

        return

    @classmethod
    def tearDownClass(self):
        """ Tear down to run basic repo tests. """
        # We now reomve the directories created from
        # running this test.
        self.repository.removeRepository()
        shutil.rmtree(self.pathToApplications)

        return

    def test_git_repo(self):
        """ Test if a sparse checkout can be performed for a git repository.
        """
        # Create the list of folders to sparsely checkout from the repository.
        self.folders0 = create_list_of_folders_to_checkout_0(self)


        with open(self.stdout_path['sparse_checkout'],"a") as stdout_handle:
            with open(self.stderr_path['sparse_checkout'],"a") as stderr_handle:
                self.repository.doSparseCheckout(stdout_file_handle=stdout_handle,
                                                 stderr_file_handle=stderr_handle,
                                                 root_path_to_checkout_directory=self.pathToApplications,
                                                 directory_to_checkout = self.folders0)

        (test_result,msg) = verify_sparse_checkout(self)
        self.assertTrue(test_result, msg)

        #Now check out new folders and verify that the new and old folders
        # exist.
        self.folders1 = create_list_of_folders_to_checkout_1(self)
        with open(self.stdout_path['sparse_checkout'],"a") as stdout_handle:
            with open(self.stderr_path['sparse_checkout'],"a") as stderr_handle:
                self.repository.doSparseCheckout(stdout_file_handle=stdout_handle,
                                                 stderr_file_handle=stderr_handle,
                                                 root_path_to_checkout_directory=self.pathToApplications,
                                                 directory_to_checkout = self.folders1)

        (test_result,msg) = verify_sparse_checkout(self)
        self.assertTrue(test_result,msg)

        self.folders2 = create_list_of_folders_to_checkout_2(self)
        with open(self.stdout_path['sparse_checkout'],"a") as stdout_handle:
            with open(self.stderr_path['sparse_checkout'],"a") as stderr_handle:
                self.repository.doSparseCheckout(stdout_file_handle=stdout_handle,
                                                 stderr_file_handle=stderr_handle,
                                                 root_path_to_checkout_directory=self.pathToApplications,
                                                 directory_to_checkout = self.folders2)

        (test_result,msg) = verify_sparse_checkout(self)
        self.assertTrue(test_result,msg)
        return

def get_path_local_repository_directory():
    path_head = os.getenv('PATH_TO_TEST_GIT_REPOSITORY')
    internal_path_applications_directory = os.getenv('PATH_RELATIVE_PATH_TO_APPS_WRT_TEST_GIT_REPOSITORY')
    return (path_head,internal_path_applications_directory)

def get_path_to_test_repository():
    path_head = os.getenv('PATH_TO_TEST_GIT_REPOSITORY')
    return path_head

def create_list_of_folders_to_checkout_0(self):
    """ Returns a dictionary of the folders/files to sparsely checkout.
    """
    my_repository_location = self.repository.getLocationOfRepository()
    
    my_repository_application = self.repository.getLocationOfFile("HelloWorld")
    tmp_words = my_repository_application.split(my_repository_location)
    my_relative_path_repository_application = tmp_words[-1]
    
    my_repository_source = self.repository.getLocationOfFile('HelloWorld/Source')
    tmp_words = my_repository_source.split(my_repository_location)
    my_relative_path_repository_source = tmp_words[-1]
    
    folders = { "application" : my_relative_path_repository_application,
                "source": my_relative_path_repository_source,
                "test" : []}

    return folders

def create_list_of_folders_to_checkout_1(self):
    """ Returns a dictionary of the folders/files to sparsely checkout.
    """
    my_repository_location = self.repository.getLocationOfRepository()
    
    my_repository_application = self.repository.getLocationOfFile("HelloWorld")
    tmp_words = my_repository_application.split(my_repository_location)
    my_relative_path_repository_application = tmp_words[-1]
    
    my_repository_source = self.repository.getLocationOfFile('HelloWorld/Source')
    tmp_words = my_repository_source.split(my_repository_location)
    my_relative_path_repository_source = tmp_words[-1]
    
    my_repository_test2 = self.repository.getLocationOfFile('HelloWorld/Test_32cores')
    tmp_words = my_repository_test2.split(my_repository_location)
    my_relative_path_repository_test2 = tmp_words[-1]
    
    folders = { "application" : my_relative_path_repository_application,
                "source": my_relative_path_repository_source,
                "test" : [my_relative_path_repository_test2]}

    return folders

def create_list_of_folders_to_checkout_2(self):
    """ Returns a dictionary of the folders/files to sparsely checkout.
    """
    my_repository_location = self.repository.getLocationOfRepository()
    
    my_repository_application = self.repository.getLocationOfFile("HelloWorld")
    tmp_words = my_repository_application.split(my_repository_location)
    my_relative_path_repository_application = tmp_words[-1]
    
    my_repository_source = self.repository.getLocationOfFile('HelloWorld/Source')
    tmp_words = my_repository_source.split(my_repository_location)
    my_relative_path_repository_source = tmp_words[-1]
    
    my_repository_test2 = self.repository.getLocationOfFile('HelloWorld/Test_32cores')
    tmp_words = my_repository_test2.split(my_repository_location)
    my_relative_path_repository_test2 = tmp_words[-1]
    
    my_repository_test1 = self.repository.getLocationOfFile('HelloWorld/Test_16cores')
    tmp_words = my_repository_test1.split(my_repository_location)
    my_relative_path_repository_test1 = tmp_words[-1]
    
    folders = { "application" : my_relative_path_repository_application,
                "source": my_relative_path_repository_source,
                "test" : [my_relative_path_repository_test2,my_relative_path_repository_test1]}

    return folders

def verify_sparse_checkout(self):
    (msg,test_result) = self.repository.verifySparseCheckout()
    return(test_result,msg)

if __name__ == "__main__":
    unittest.main()
