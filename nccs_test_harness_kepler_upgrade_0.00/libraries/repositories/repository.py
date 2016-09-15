from abc import ABCMeta
from abc import abstractmethod

class SVNRepository:
    def __init__(self,
                 location_of_repository=None):

        self.__binaryName = "svn"
        self.__locationOfRepository = location_of_repository

        pass

    def doSparseCheckout(self):
        print("From SVNRepository: Stud message for doing a sparse checkout")

class GitRepository:
    def __init__(self,
                 location_of_repository=None):

        self.__binaryName = "git"
        self.__locationOfRepository = location_of_repository

    def doSparseCheckout(self):
        print("From GitRepository: Stud message for doing a sparse checkout")

class BaseRepository(metaclass=ABCMeta):
    @abstractmethod
    def doSparseCheckout(self):
        print("From BaseRepository: Stud message for doing a sparse checkout")


BaseRepository.register(SVNRepository)
BaseRepository.register(GitRepository)
