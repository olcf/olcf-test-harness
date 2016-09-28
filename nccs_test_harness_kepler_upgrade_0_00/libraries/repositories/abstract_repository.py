from abc import ABCMeta
from abc import abstractmethod

# NCCS Tesst Harness packages

class BaseRepository(metaclass=ABCMeta):
    """ This class define the comman behavoir of a repository as expected by the NCCS Test Harness.

    """
    def __init__(self):
        print("In base repository")
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

    @abstractmethod
    def removeRepository(self):
        return

    @abstractmethod
    def doSparseSourceCheckout(self)
        return

