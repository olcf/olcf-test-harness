#! /usr/bin/env python3

# System imports


# Local package imports


class RepositoryFactoryError(Exception):
    """ Base class exception for this module. """
    def __init__(self):
        return

    def what(self):
        self.whatIsMyError()

class TypeOfRepositoryError(RepositoryFactoryError):
    """Exception raised when an invalid repository type is specified

    Attributes:
        expression -- the type of repository the error occured
        message -- explanation of error
    """

    def __init__(self,
                 expression=None,
                 message=None):
        self.expression = expression
        self.mesage = message

    def whatIsMyError(self):
        message = "Stud message for TypeOfRepositoryError.\n"
        print(message)

