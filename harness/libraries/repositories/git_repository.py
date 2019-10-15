#!/usr/bin/env python3

import os

# NCCS Tesst Harness packages
from libraries.repositories.common_repository_utility_functions import run_as_subprocess_command
from libraries.repositories.common_repository_utility_functions import run_as_subprocess_command_return_stdout_stderr
from libraries.repositories.abstract_repository import BaseRepository


class GitRepository(BaseRepository):
    """ This class is encapsulates the behavoir of a git repository.
    """
    def __init__(self,
                 git_remote_repository_url=None,
                 my_repository_branch="master") :

        
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
                        destination_directory="."):

        my_clone_command="{gitbinary} clone --branch {branch} --recurse-submodules {repository} {directory}".format(
                  gitbinary=self.binaryName,
                  branch=self.repository_branch, 
                  repository=self.remote_repository_URL,
                  directory=destination_directory)

        run_as_subprocess_command(my_clone_command)
        return

def get_type_of_repository():
    return os.getenv('RGT_TYPE_OF_REPOSITORY')

def get_application_parent_directory():
    parent_path=os.getenv("RGT_GIT_SERVER_APPLICATION_PARENT_DIR")
    return parent_path

def get_fully_qualified_url_of_application_parent_directory():
    my_machine = os.getenv("RGT_GIT_MACHINE_NAME")
    parent_directory=get_application_parent_directory() + "/" + my_machine + "/"

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

def get_repository_url_of_application(application):
    my_machine = os.getenv("RGT_GIT_MACHINE_NAME")
    parent_directory = get_application_parent_directory()

    data_transfer_protocol = os.getenv("RGT_GIT_DATA_TRANSFER_PROTOCOL")

    if  data_transfer_protocol == "ssh" :
        my_git_server_url=os.getenv("RGT_GIT_SSH_SERVER_URL")
        path1 = my_git_server_url + ":" + parent_directory + "/"
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

def get_repository_git_branch():
    my_git_branch=os.getenv("RGT_GIT_REPS_BRANCH")
    return my_git_branch
