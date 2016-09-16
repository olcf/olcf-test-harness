from abc import ABCMeta
from abc import abstractmethod
import shutil

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
        shutil.copytree(path_to_sample_directory,path_to_local_dir)

        return

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
        shutil.copytree(path_to_sample_directory,path_to_local_dir)
        return

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
