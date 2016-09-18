from abc import ABCMeta
from abc import abstractmethod
import shutil
import os
import subprocess

class SVNRepository:
    """ This class is encapsulates the behavoir of a svn repository.

    """

    def __init__(self,
                 location_of_repository=None):
        self.__binaryName = "svn"
        self.__locationOfRepository = location_of_repository
        return

    @classmethod
    def createLocalRepoFromExistingDirectory(cls,
                                             path_to_sample_directory,
                                             path_to_local_dir):
        completed_svn_init = subprocess.run(["svnadmin","create",path_to_local_dir])
        svn_url = "file://" + path_to_local_dir + "/trunk/"
        subprocess.run(["svn","import",path_to_sample_directory,svn_url,"-m 'Initial svn commit'"])
        return RepositoryFactory.create("svn",
                                         svn_url)
    def getLocationOfRepository(self):
        return self.__locationOfRepository

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

            :param directory_to_checkout: A list of directories or files to sparsely checkout.
            :type directories: a string list of directory or file names.

            :returns: a tuple (message,exit_status) 
            :rtype:  message is a string, exit_status is an integer
        """
        # Check if file handles are open
        message = ""
        if stdout_file_handle.closed:
            message =  "Error! In sparse checkout the stdout file handle is closed"
            exit_status = 1
            return (message,exit_status)

        if stderr_file_handle.closed:
            message =  "Error! In sparse checkout the stderr file handle is closed"
            exit_status = 1
            return (message,exit_status)

        # Define the svn options for a sparse checkout.
        svn_options = 'checkout -N'
       
        # Define the full qualified path the checkout location of the folder.
        tail_dir = os.path.basename(directory_to_checkout)
        path_to_local_dir = os.path.join(root_path_to_checkout_directory,tail_dir)

        # Form the checkout command
        sparse_checkout_command = "{my_bin} {my_options} {my_svn_path} {my_local_path}".format(
                                            my_bin = self.__binaryName, 
                                            my_options = svn_options, 
                                            my_svn_path = directory_to_checkout,
                                            my_local_path = path_to_local_dir)

        exit_status = subprocess.call(sparse_checkout_command,
                                      shell=True,
                                      stdout=stdout_file_handle,
                                      stderr=stderr_file_handle)

        if exit_status > 0:
            message = "Sparse checkout of command failed: " + sparse_checkout_command

        return (message,exit_status)

class GitRepository:
    """ This class is encapsulates the behavoir of a git repository.

    """
    def __init__(self,
                 location_of_repository=None):
        self.__binaryName = "git"
        self.__locationOfRepository = location_of_repository
        return

    @classmethod
    def createLocalRepoFromExistingDirectory(cls,
                                        path_to_sample_directory,
                                        path_to_local_dir):
        starting_directory = os.getcwd()
        shutil.copytree(path_to_sample_directory,path_to_local_dir)
        
        os.chdir(path_to_local_dir)
        completed_git_init = subprocess.run(["git","init"])

        completed_git_add = subprocess.run(["git","add","."])

        completed_git_commit = subprocess.run(["git","commit","-m", "My git commit"])

        os.chdir(starting_directory )

        return RepositoryFactory.create("git",path_to_local_dir)

    def getLocationOfRepository(self):
        return self.__locationOfRepository

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

            :param directory_to_checkout: A list of directories or files to sparsely checkout.
            :type directories: a string list of directory or file names.

            :returns: a tuple (message,exit_status) 
            :rtype:  message is a string, exit_status is an integer
        """
        
        # Check if file handles are open
        message = ""
        if stdout_file_handle.closed:
            message =  "Error! In sparse checkout the stdout file handle is closed"
            exit_status = 1
            return (message,exit_status)

        if stderr_file_handle.closed:
            message =  "Error! In sparse checkout the stderr file handle is closed"
            exit_status = 1
            return (message,exit_status)
        return

class BaseRepository(metaclass=ABCMeta):
    """ This class define the comman behavoir of a repository as expected by the NCCS Test Harness.

    """

    @classmethod
    @abstractmethod
    def createLocalRepoFromExistingDirectory(cls):
        return

    @abstractmethod
    def doSparseCheckout(self):
        return

    @abstractmethod
    def getLocationOfRepository(self):
        return

BaseRepository.register(SVNRepository)
BaseRepository.register(GitRepository)

class RepositoryFactory:
    """ This class is a factory that creates repository objects.

    This class creates a repository object by calling the class method
    create. Currently only git and svn repository objects are supported.
    """
    def __init__(self):
        return

    @classmethod
    def create(cls,
               type_of_repository,
               location_of_repository):
        """ Creates a repository object that encapuslates the repository behavoir. 

        This class method will a Repository object if the type_of_repository is 
        supported, othewise a value of None will be returned. 

        :param type_of_repository: The type of repositiory
        :type type_of_repository: string

        :param location_of_repository: The fully qualified path to an existing repository.
        :type location_of_repository: string

        :returns: my_repository
        :rtype: A Repository object - currently only GitRepository or SVNRepository objects 
                are returned. 
        """

        # Check if the repository string value in type_of_repository 
        # matches one of the supported types.  
        my_repository = None
        if type_of_repository == "git":
            my_repository = GitRepository(location_of_repository)
        elif type_of_repository == "svn":
            my_repository = SVNRepository(location_of_repository)
        else:
            # No supporting repository if program reaches this branch.
            my_repository = None

        return my_repository

