#! /usr/bin/env python3

# System imports

# Local package imports
class GitActionException(Exception):
    """ Base class exception for this module. """
    def __init__(self):
        return

    def what(self):
        self.whatIsMyError()

class CloningToDirectoryWithIncorrectOriginError(GitActionException):
    """Exception raised when cloning to a directory that exists.

    Attributes:
        expression -- the type of repository the error occured
        message -- explanation of error
    """

    def __init__(self,
                 message=None):
        self.mesage = message

    def whatIsMyError(self):
        print(self.message)

