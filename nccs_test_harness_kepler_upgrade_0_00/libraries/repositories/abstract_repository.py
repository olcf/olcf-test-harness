from abc import ABCMeta
from abc import abstractmethod

# NCCS Tesst Harness packages
from .repository import SVNRepository
from .repository import GitRepository

class BaseRepository(metaclass=ABCMeta):
    """ This class define the comman behavoir of a repository as expected by the NCCS Test Harness.

    """
    def __init__(self):
        print("In base repository")
        return

    @classmethod
    @abstractmethod
    def createLocalRepoFromExistingDirectory(cls):
        return

    @abstractmethod
    def doSparseCheckout(self):
        return

    @abstractmethod
    def verifySparseCheckout(self):
        return

    @abstractmethod
    def getLocationOfRepository(self):
        return

    @abstractmethod
    def getLocationOfFile(self):
        return

BaseRepository.register(SVNRepository)
BaseRepository.register(GitRepository)

