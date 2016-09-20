#! /usr/bin/env python3
""" Test class module verifies repositories encapsulation works.  """

import unittest
import os
import shutil

from libraries.repositories.repository import SVNRepository
from libraries.repositories.repository import GitRepository


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
            get_path_local_repository_directory("git")

        self.repository = GitRepository.createLocalRepoFromExistingDirectory(path_to_sample_directory,
                                                                             path_to_test_repository)

        ## Make the application directory - this directory will contain the sparse
        ## checkout of the Application and test.
        #self.pathToApplications = get_path_to_application_directory("git_sparse_checkout_applications")
        #create_application_directory(self)

        ## Define the path to the repository.
        #self.pathToRepository = os.environ["RGT_PATH_TO_REPS"]

        ## Create the list of folders to sparsely checkout from the repository.
        #self.folders = create_list_of_folders_to_checkout(self)
        return

    def tearDown(self):
        """ Tear down to run basic repo tests. """
        return


    def test_git_repo(self):
        # Do a sparse chekout of the of Hello Word test Test16_cores.
        # from the directory "Sample_Directory_For_Repository_Testing"
        with open(self.stdout_path['sparse_checkout'],"a") as stdout_handle:
            with open(self.stderr_path['sparse_checkout'],"a") as stderr_handle:
                self.repository.doSparseCheckout(stdout_file_handle=stdout_handle,
                                                 stderr_file_handle=stderr_handle,
                                                 path_to_repository=self.pathToRepository,
                                                 root_path_to_checkout_directory=self.pathToApplications,
                                                 directory_to_checkout = self.folders[0])

        (test_result,msg) = verify_sparse_checkout(self)
        self.assertTrue(test_result, msg)

        return


class Test_SVN_repositories(unittest.TestCase):
    """ Tests for repository functionality """

    def setUp(self):
        """ Set up to run basic repository tests. """

        # Define standard oaut and error file names for commands
        self.stdout_path = {'sparse_checkout' : os.path.join( os.path.abspath('.'), 'svn_sparse_checkout.stdout.txt')}
        self.stderr_path = {'sparse_checkout' : os.path.join( os.path.abspath('.'), 'svn_sparse_checkout.stderr.txt')}

        # Make a local svn repository
        path_to_sample_directory = get_path_to_sample_directory()
        (path_to_test_repository,path_relative_path_to_apps_wrt_test_git_repository) = \
            get_path_local_repository_directory("svn")
        self.repository = SVNRepository.createLocalRepoFromExistingDirectory(path_to_sample_directory,
                                                                             path_to_test_repository)

        ## Make the application directory - this directory will contain the sparse
        ## checkout of the Application and test.
        #self.pathToApplications = get_path_to_application_directory("svn_sparse_checkout_applications")
        #create_application_directory(self)

        ## Define the path to the repository.
        #self.pathToRepository = os.environ["RGT_PATH_TO_REPS"]

        ## Create the list of folders to sparsely checkout from the repository.
        #self.folders = create_list_of_folders_to_checkout(self)

        return

    def tearDown(self):
        """ Tear down to run basic repo tests. """
        return

    def test_svn_repo(self):
        # Do a sparse chekout of the of file_1.txt
        # from the directory "Sample_Directory_For_Repository_Testing"
        with open(self.stdout_path['sparse_checkout'],"a") as stdout_handle:
            with open(self.stderr_path['sparse_checkout'],"a") as stderr_handle:
                self.repository.doSparseCheckout(stdout_file_handle=stdout_handle,
                                                 stderr_file_handle=stderr_handle,
                                                 path_to_repository=self.pathToRepository,
                                                 root_path_to_checkout_directory=self.pathToApplications,
                                                 directory_to_checkout = self.folders[0])

        (test_result,msg) = verify_sparse_checkout(self)
        self.assertTrue(test_result, msg)
        return


def get_path_to_sample_directory():
    """ Returns the fully qualified path to the directory 'Sample_Directory_For_Repository_Testing'
    """
    path_head = os.getenv('PATH_TO_HARNESS_TOP_LEVEL')
    path_to_dir = os.path.join(
        path_head, 'test', 'input_files', 'Sample_Directory_For_Repository_Testing')
    return path_to_dir

def get_path_to_application_directory(tag):
    path_head = os.path.abspath('.')
    path_to_dir = os.path.join(path_head,tag)
    return path_to_dir

def get_path_local_repository_directory(tag):
    path_head = None
    if tag == 'git':
        path_head = os.getenv('PATH_TO_TEST_GIT_REPOSITORY')
        internal_path_applications_directory = os.getenv('PATH_RELATIVE_PATH_TO_APPS_WRT_TEST_GIT_REPOSITORY')
    elif tag == 'svn':
        path_head = os.getenv('PATH_TO_TEST_SVN_REPOSITORY')
        internal_path_applications_directory = os.getenv('PATH_RELATIVE_PATH_TO_APPS_WRT_TEST_SVN_REPOSITORY')
    return (path_head,internal_path_applications_directory)

def create_application_directory(my_unit_test):
    if os.path.exists(my_unit_test.pathToApplications) :
        shutil.rmtree(my_unit_test.pathToApplications)
    os.makedirs(my_unit_test.pathToApplications)
    return

def create_list_of_folders_to_checkout(self):
    my_repository_location = self.repository.getLocationOfRepository()
    folders = [
                os.path.join(my_repository_location,'Test_16cores'),
              ]
    return folders

def verify_sparse_checkout(self):
    msg = "Stud message"
    test_result = False
    return(test_result,msg)

if __name__ == "__main__":
    unittest.main()
