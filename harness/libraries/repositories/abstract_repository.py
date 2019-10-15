from abc import ABCMeta
from abc import abstractmethod

# NCCS Tesst Harness packages

class BaseRepository(metaclass=ABCMeta):
    """ This class define the comman behavoir of a repository as expected by the NCCS Test Harness.

    """
    def __init__(self):
        return

    @classmethod
    @abstractmethod
    def get_application_parent_directory(cls):
        return

    @classmethod
    @abstractmethod
    def get_repository_url_of_application(cls,application):
        return

    @classmethod
    @abstractmethod
    def get_fully_qualified_url_of_application_parent_directory():
        return

    @property
    @abstractmethod
    def binaryName(self):
        return 

    @binaryName.setter
    @abstractmethod
    def binaryName(self,value):
        return

    @property 
    @abstractmethod
    def repository_branch(self):
        return self.__repositoryBranch
    
    @repository_branch.setter
    @abstractmethod
    def repository_branch(self,value):
        return
    
    @property
    @abstractmethod
    def remote_repository_URL(self):
        return 

    @remote_repository_URL.setter
    @abstractmethod
    def remote_repository_URL(self,value):
        return


    @abstractmethod
    def cloneRepository(self):
        return

