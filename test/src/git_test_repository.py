#! /usr/bin/env python3
""" Test class module verifies repositories encapsulation works.  """

import unittest
import os
import shutil

# NCCS Test Harness package imports
from libraries.repositories.repository_factory import RepositoryFactory


class Test_Git_repositories(unittest.TestCase):
    """ Tests for repository functionality

        This class tests if the git repository class can
        do sparse checkout.

    """

    def setUp(self):
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

        # Make the application directory - this directory will contain the sparse
        # checkout of the Application and test.
        self.pathToApplications = get_path_to_application_directory("git_sparse_checkout_applications")
        create_application_directory(self)

        # Define the path to the repository.
        self.pathToRepository = get_path_to_test_repository()

        # Create the list of folders to sparsely checkout from the repository.
        self.folders = create_list_of_folders_to_checkout(self)
        return

    def tearDown(self):
        """ Tear down to run basic repo tests. """
        return

    def test_git_repo(self):
        """ Test is a sparse checkout can be performed for a git repository.

        """
        with open(self.stdout_path['sparse_checkout'],"a") as stdout_handle:
            with open(self.stderr_path['sparse_checkout'],"a") as stderr_handle:
                self.repository.doSparseCheckout(stdout_file_handle=stdout_handle,
                                                 stderr_file_handle=stderr_handle,
                                                 path_to_repository=self.pathToRepository,
                                                 root_path_to_checkout_directory=self.pathToApplications,
                                                 directory_to_checkout = self.folders)

        (test_result,msg) = verify_sparse_checkout(self)
        self.assertTrue(test_result, msg)

        return

def get_path_to_sample_directory():
    """ Returns the fully qualified path to the directory 'Sample_Directory_For_Repository_Testing'


        :returns: path_to_dir, The path to the directory which is used for creating the test repository.    
        :rtype:  string
    """
    path_head = os.getenv('PATH_TO_HARNESS_TOP_LEVEL')
    path_to_dir = os.path.join(
        path_head, 'test', 'input_files', 'Sample_Directory_For_Repository_Testing')
    return path_to_dir

def get_path_to_application_directory(tag):
    """ Returns the fully qualified path to the directory which will serve as the root for the checkedout applications. 

        :returns:  path_to_dir, The path to the directory which will serve as the root for the checkedout applications. 
        :rtype:  string
    """
    path_head = os.path.abspath('.')
    path_to_dir = os.path.join(path_head,tag)
    return path_to_dir

def get_path_local_repository_directory():
    path_head = os.getenv('PATH_TO_TEST_GIT_REPOSITORY')
    internal_path_applications_directory = os.getenv('PATH_RELATIVE_PATH_TO_APPS_WRT_TEST_GIT_REPOSITORY')
    return (path_head,internal_path_applications_directory)

def get_path_to_test_repository():
    path_head = os.getenv('PATH_TO_TEST_GIT_REPOSITORY')
    return path_head

def create_application_directory(my_unit_test):
    if os.path.exists(my_unit_test.pathToApplications) :
        shutil.rmtree(my_unit_test.pathToApplications)
    os.makedirs(my_unit_test.pathToApplications)
    return

def create_list_of_folders_to_checkout(self):
    """ Returns a dictionary of the folders/files to sparsely checkout.
    """
    my_repository_location = self.repository.getLocationOfRepository()
    
    my_repository_application = self.repository.getLocationOfFile("HelloWorld")
    tmp_words = my_repository_application.split(my_repository_location)
    my_relative_path_repository_application = tmp_words[-1]
    
    
    my_repository_test1 = self.repository.getLocationOfFile('HelloWorld/Test_16cores')
    tmp_words = my_repository_test1.split(my_repository_location)
    my_relative_path_repository_test1 = tmp_words[-1]
    
    my_repository_test2 = self.repository.getLocationOfFile('HelloWorld/Test_32cores')
    tmp_words = my_repository_test2.split(my_repository_location)
    my_relative_path_repository_test2 = tmp_words[-1]
    
    my_repository_source = self.repository.getLocationOfFile('HelloWorld/Source')
    tmp_words = my_repository_source.split(my_repository_location)
    my_relative_path_repository_source = tmp_words[-1]
    
    folders = { "application" : my_relative_path_repository_application,
                "source": my_relative_path_repository_source,
                "test" : [my_relative_path_repository_test1, my_relative_path_repository_test2]}

    return folders

def verify_sparse_checkout(self):
    (msg,test_result) = self.repository.verifySparseCheckout()
    return(test_result,msg)

if __name__ == "__main__":
    unittest.main()
