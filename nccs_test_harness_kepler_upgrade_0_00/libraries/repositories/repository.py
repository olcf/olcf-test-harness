from abc import ABCMeta
from abc import abstractmethod
import shutil
import os
import subprocess

class SVNRepository:
    def __init__(self,
                 location_of_repository=None):
        self.__binaryName = "svn"
        self.__locationOfRepository = location_of_repository
        return

    @classmethod
    def createRepoFromExistingDirectory(cls,
                                        path_to_sample_directory,
                                        path_to_local_dir):
        completed_svn_init = subprocess.run(["svnadmin","create",path_to_local_dir])
        svn_url = "file://" + path_to_local_dir + "/trunk"
        subprocess.run(["svn","import",path_to_sample_directory,svn_url,"-m 'Initial svn commit'"])
        
        return RepositoryFactory.create("svn",svn_url)

    def doSparseCheckout(self):
        return

class GitRepository:
    def __init__(self,
                 location_of_repository=None):
        self.__binaryName = "git"
        self.__locationOfRepository = location_of_repository
        return

    @classmethod
    def createRepoFromExistingDirectory(cls,
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


    def doSparseCheckout(self):
        return

class BaseRepository(metaclass=ABCMeta):

    @classmethod
    @abstractmethod
    def createRepoFromExistingDirectory(cls):
        return

    @abstractmethod
    def doSparseCheckout(self):
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

