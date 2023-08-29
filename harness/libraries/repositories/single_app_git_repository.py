#!/usr/bin/env python3

import enum
import os

# NCCS Tesst Harness packages
from libraries.repositories.common_repository_utility_functions import run_as_subprocess_command
from libraries.repositories.common_repository_utility_functions import run_as_subprocess_command_return_stdout_stderr
from libraries.repositories.abstract_repository import BaseRepository
from libraries.repositories.git_repository_exceptions import CloningToDirectoryWithIncorrectOriginError

@enum.unique
class GitCloneFlag(enum.Enum):
    DIRECTORY_NOT_FOUND = enum.auto()
    FOUND_EXISTING_DIRECTORY = enum.auto()
    FOUND_EXISTING_REPOSITORY_WITH_INCORRECT_ORIGIN = enum.auto()
    FOUND_EXISTING_REPOSITORY_WITH_CORRECT_ORIGIN = enum.auto()
   
class SingleApplicationGitRepository(BaseRepository):
    """ This class is encapsulates the behavoir of a git repository.
    """

    @classmethod
    def get_application_parent_directory(cls):
        parent_path=os.getenv("RGT_GIT_SERVER_APPLICATION_PARENT_DIR")
        return parent_path

    @classmethod
    def get_repository_url_of_application(cls,application):
        my_machine = os.getenv("RGT_GIT_MACHINE_NAME")
        parent_directory = cls.get_application_parent_directory()

        data_transfer_protocol = os.getenv("RGT_GIT_DATA_TRANSFER_PROTOCOL")

        if  data_transfer_protocol == "ssh" :
            my_git_server_url=os.getenv("RGT_GIT_SSH_SERVER_URL")
            path1 = my_git_server_url + ":" + parent_directory + "/" + my_machine + "/"
            path2 = application + ".git"
            git_url_to_remote_repsitory_application = path1 + path2
        elif data_transfer_protocol == "https":
            my_git_server_url=os.getenv("RGT_GIT_HTTPS_SERVER_URL")
            path1 = my_git_server_url + "/" + parent_directory + "/"
            path2 = application + ".git"
            git_url_to_remote_repsitory_application = path1 + path2
        else :
            # To Do: Raise exception for there are only two types of data transfer protocol.
            git_url_to_remote_repsitory_application = "no_valid_path"

        return git_url_to_remote_repsitory_application

    @classmethod
    def get_fully_qualified_url_of_application_parent_directory(cls):
        my_machine = os.getenv("RGT_GIT_MACHINE_NAME")
        parent_directory=cls.get_application_parent_directory() + "/" + my_machine + "/"

        data_transfer_protocol = os.getenv("RGT_GIT_DATA_TRANSFER_PROTOCOL")

        if  data_transfer_protocol == "ssh" :
            my_git_server_url=os.getenv("RGT_GIT_SSH_SERVER_URL")
            path1 = my_git_server_url + ":" + parent_directory 
        elif data_transfer_protocol == "https" :
            my_git_server_url=os.getenv("RGT_GIT_HTTPS_SERVER_URL")
            path1 = my_git_server_url + "/" + parent_directory
        else :
            # To Do: Raise exception for there are only two types of data transfer protocol.
            path1 = "no_valid_path: To do : raise exception"

        return path1

    def __init__(self,
                 git_remote_repository_url=None,
                 my_repository_branch="default") :

        
        self.binaryName = "git"
        self.remote_repository_URL = git_remote_repository_url
        self.repository_branch = my_repository_branch
        return

    @property
    def binaryName(self):
        return self.__binaryName
    
    @binaryName.setter
    def binaryName(self,value):
        self.__binaryName = value
        return

    @property 
    def repository_branch(self):
        return self.__repositoryBranch
    
    @repository_branch.setter
    def repository_branch(self,value):
        self.__repositoryBranch = value
        return
    
    @property
    def remote_repository_URL(self):
        return self.__gitRemoteRepositoryURL

    @remote_repository_URL.setter
    def remote_repository_URL(self,value):
        self.__gitRemoteRepositoryURL = value
        return
    
    def cloneRepository(self,
                        destination_directory=".",
                        logger=None):


        clone_branch = ""
        if self.repository_branch != "default":
            clone_branch = f'--branch {self.repository_branch}'

        my_clone_command="{gitbinary} clone {branch} --recurse-submodules {repository}".format(
                  gitbinary=self.binaryName,
                  branch=clone_branch,
                  repository=self.remote_repository_URL)

        basename = os.path.basename(self.remote_repository_URL)
        (dirname,extension) = os.path.splitext(basename)
        pathspec = os.path.join(destination_directory,dirname)
        
        clone_flag = self.__checkDirectoryForCloning(pathspec,
                                                     self.remote_repository_URL)
        
        if clone_flag == GitCloneFlag.DIRECTORY_NOT_FOUND:
            os.makedirs(pathspec)
            run_as_subprocess_command(my_clone_command,
                                      command_execution_directory=destination_directory)

        elif clone_flag == GitCloneFlag.FOUND_EXISTING_REPOSITORY_WITH_CORRECT_ORIGIN:
            message = "The directory {} exists and is already cloned. Therefore we will will skip cloning repository {}.\n".format(pathspec,
                                                                                                                                   self.remote_repository_URL)
            logger.doWarningLogging(message)
        elif clone_flag == GitCloneFlag.FOUND_EXISTING_REPOSITORY_WITH_INCORRECT_ORIGIN:
            message = "The directory {} is an existing git repository whose origin is not {}.\n".format(pathspec,
                                                                                                        self.remote_repository_URL)
            logger.doWarningLogging(message)
            raise CloningToDirectoryWithIncorrectOriginError(message)
                
        return 

    def __checkDirectoryForCloning(self,
                                   pathspec,
                                   repository_url):
        
        dir_clone_status = GitCloneFlag.DIRECTORY_NOT_FOUND

        # Check if the directory exists.
        if os.path.lexists(pathspec) :
            dir_clone_status = GitCloneFlag.FOUND_EXISTING_DIRECTORY 
        else:
            dir_clone_status = GitCloneFlag.DIRECTORY_NOT_FOUND 

        if dir_clone_status == GitCloneFlag.FOUND_EXISTING_DIRECTORY:
            my_command = "git config --get remote.origin.url"
            (stdout,stderr) = run_as_subprocess_command_return_stdout_stderr(my_command,pathspec)
            if len(stdout) >= 1:
                if stdout[0].rfind(repository_url) == 0:
                    dir_clone_status = GitCloneFlag.FOUND_EXISTING_REPOSITORY_WITH_CORRECT_ORIGIN
                else:
                    dir_clone_status = GitCloneFlag.FOUND_EXISTING_REPOSITORY_WITH_INCORRECT_ORIGIN
            else:
                dir_clone_status = GitCloneFlag.FOUND_EXISTING_REPOSITORY_WITH_INCORRECT_ORIGIN

        return dir_clone_status
