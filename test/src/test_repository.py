#! /usr/bin/env python3
""" Test class module verifies repositories encapsulation works.  """

import unittest
import os

from libraries.repositories.repository import SVNRepository
from libraries.repositories.repository import GitRepository


class Test_Git_repositories(unittest.TestCase):
    """ Tests for repository functionality

        This class tests if the git repository class can
        do sparse checkout.

    """

    def setUp(self):
        """ Set up to run basic repository tests. """

        # Make a local git repository
        path_to_sample_directory = get_path_to_sample_directory()
        local_dir = get_path_to_local_dir("git_repo")
        self.repository = GitRepository.createLocalRepoFromExistingDirectory(path_to_sample_directory,
                                                                             local_dir)

        return

    def tearDown(self):
        """ Tear down to run basic repo tests. """
        return


    def test_git_repo(self):
        # Do a sparse chekout of the of file_1.txt
        # from the directory "Sample_Directory_For_Repository_Testing"
        self.repository.doSparseCheckout()

        msg = "Stud message for git repository."
        self.assertTrue(False, msg)
        return


class Test_SVN_repositories(unittest.TestCase):
    """ Tests for repository functionality """

    def setUp(self):
        """ Set up to run basic repository tests. """

        # Make a local svn repository
        path_to_sample_directory = get_path_to_sample_directory()
        local_dir = get_path_to_local_dir("svn_repo")
        self.repository = SVNRepository.createLocalRepoFromExistingDirectory(path_to_sample_directory,
                                                                             local_dir)
        return

    def tearDown(self):
        """ Tear down to run basic repo tests. """
        return

    def test_svn_repo(self):
        # Do a sparse chekout of the of file_1.txt
        # from the directory "Sample_Directory_For_Repository_Testing"
        self.repository.doSparseCheckout()

        msg = "Stud message for svn repository."
        self.assertTrue(False, msg)
        return


def get_path_to_sample_directory():
    path_head = os.getenv('PATH_TO_HARNESS_TOP_LEVEL')
    path_to_dir = os.path.join(
        path_head, 'test', 'input_files', 'Sample_Directory_For_Repository_Testing')
    return path_to_dir


def get_path_to_local_dir(tag):
    path_head = os.getcwd()
    path_to_dir = os.path.join(path_head, "local_repository", tag)
    return path_to_dir

if __name__ == "__main__":
    unittest.main()
