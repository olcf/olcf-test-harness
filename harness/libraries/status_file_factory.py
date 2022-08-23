#! /usr/bin/env python3
"""The factory class creating StatusFile objects."""

# Python imports
import sys

# Harness imports
from libraries.status_file import StatusFile

class StatusFileFactory:
    """This is the factory class of StatusFile objects."""

    #-----------------------------------------------------
    #                                                    -
    # Class attributes and methods.                      -
    #                                                    -
    #-----------------------------------------------------
    @classmethod
    def create(cls,path_to_status_file=None,logger=None, test_id=None):
        """ Returns a StatusFile object.

        Notes
        -----
        This factory method is called if we are creating a StatusFile object

        Parameters
        ----------
        path_to_status_file : str 
            The fully qualified path to the status file.

        Returns
        -------
        StatusFile
        """
        a_status_file = StatusFile(logger=logger,
                                   path_to_status_file=path_to_status_file,
                                   test_id=test_id)

        return a_status_file

    #-----------------------------------------------------
    #                                                    -
    # Special methods                                    -
    #                                                    -
    #-----------------------------------------------------
    def __init__(self):
        pass

    
    #-----------------------------------------------------
    #                                                    -
    # Public methods                                     -
    #                                                    -
    #-----------------------------------------------------
