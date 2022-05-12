#! /usr/bin/env python3
import shutil
import sys
import os
import subprocess
import logging

# NCCS Test Harness package imports
from libraries.repositories.single_app_git_repository import SingleApplicationGitRepository 
from libraries.repositories.repository_factory_exceptions import TypeOfRepositoryError

class RepositoryFactory:
    """ This class is a factory that creates repository objects.

    This class creates a repository object by calling the class method
    create. Currently only git and svn repository objects are supported.
    """
    @classmethod
    def create(cls,
               type_of_repository,
               repository_URL,
               repository_branch):
        """ Creates a repository object that encapuslates the repository behavoir. 

        This class method will a Repository object if the type_of_repository is 
        supported, othewise a value of None will be returned. 

        :param type_of_repository: The type of repositiory
        :type type_of_repository: string

        :param repository_URL: The fully qualified path to an existing repository.
        :type repository_URL: string

        :param repository branch: The name of the branch of the repository/
        :type repository_branch string 

        :returns: my_repository
        :rtype: A Repository object - currently only SingleApplicationGitRepository objects 
                are returned. 
        """

        # Check if the repository string value in type_of_repository 
        # matches one of the supported types.  
        my_repository = None
        repository_factory_log = logging.getLogger(__name__)
        try:
            if type_of_repository == "git":
                my_repository = SingleApplicationGitRepository(repository_URL,
                                                               repository_branch)
            else:
                # No supporting repository if program reaches this branch.
                my_repository = None
                msg =  "The type of repository is '{}'. This error is generally due to the\n"
                msg += "environmental variable 'RGT_TYPE_OF_REPOSITORY' not being defined or defined\n"
                msg += "to a repository type not supported by this test harness.\n\n".format("None")
                raise TypeOfRepositoryError(type_of_repository,msg)
        except TypeOfRepositoryError as error:
            msg =  "The type of repository is '%s'. This error is generally due to the \n"
            msg += "environmental variable 'RGT_TYPE_OF_REPOSITORY' not being defined or defined\n"
            msg += "to a repository type not supported by this test harness.\n\n"
            repository_factory_log.exception(msg,"None",exc_info=True,stack_info=True)
            sys.exit(1)

        return my_repository
    
    @classmethod
    def get_fully_qualified_url_of_application_parent_directory(cls):
        try:
            if cls.get_type_of_repository() == "git":
                pathspec=SingleApplicationGitRepository.get_fully_qualified_url_of_application_parent_directory()
            else:
                # No supporting repository if program reaches this branch.
                pathspec = None
                msg =  "The type of repository is '{}'. This error is generally due to the\n"
                msg += "environmental variable 'RGT_TYPE_OF_REPOSITORY' not being defined or defined\n"
                msg += "to a repository type not supported by this test harness.\n\n".format("None")
                raise TypeOfRepositoryError(type_of_repository,msg)
        except TypeOfRepositoryError as error:
            msg =  "The type of repository is '%s'. This error is generally due to the \n"
            msg += "environmental variable 'RGT_TYPE_OF_REPOSITORY' not being defined or defined\n"
            msg += "to a repository type not supported by this test harness.\n\n"
            repository_factory_log.exception(msg,"None",exc_info=True,stack_info=True)
            sys.exit(1)
        return pathspec

    @classmethod
    def get_repository_url_of_application(cls,application):
        try:
            if cls.get_type_of_repository() == "git":
                pathspec=SingleApplicationGitRepository.get_repository_url_of_application(application)
            else:
                # No supporting repository if program reaches this branch.
                pathspec = None
                msg =  "The type of repository is '{}'. This error is generally due to the\n"
                msg += "environmental variable 'RGT_TYPE_OF_REPOSITORY' not being defined or defined\n"
                msg += "to a repository type not supported by this test harness.\n\n".format("None")
                raise TypeOfRepositoryError(type_of_repository,msg)
        except TypeOfRepositoryError as error:
            msg =  "The type of repository is '%s'. This error is generally due to the \n"
            msg += "environmental variable 'RGT_TYPE_OF_REPOSITORY' not being defined or defined\n"
            msg += "to a repository type not supported by this test harness.\n\n"
            repository_factory_log.exception(msg,"None",exc_info=True,stack_info=True)
            sys.exit(1)
        return pathspec

    @classmethod
    def get_type_of_repository(cls):
        return os.getenv('RGT_TYPE_OF_REPOSITORY')

    @classmethod
    def get_repository_git_branch(cls):
        my_git_branch = os.getenv("RGT_GIT_REPS_BRANCH")
        if my_git_branch is None:
            my_git_branch = "default"
        return my_git_branch


