#! /usr/bin/env python3
"""Contains the subtest factory class SubtestFactory

This module contains the factory class SubtestFactory which 
creates an instance of subtest.

"""

# Python imports
import os

# Harness imports
from libraries.apptest import subtest


class SubtestFactory():
    """This class resposibility is creating an instance subtest."""

    #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
    #                                                                 @
    # Special methods                                                 @
    #                                                                 @
    #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
    def __init__(self):
        return

    #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
    #                                                                 @
    # End of special methods                                          @
    #                                                                 @
    #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

    #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
    #                                                                 @
    # Public methods.                                                 @
    #                                                                 @
    #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
    @staticmethod
    def make_subtest(name_of_application=None,
                     name_of_subtest=None,
                     local_path_to_tests=None,
                     logger=None,
                     db_logger=None,
                     tag=None):
        """Returns an instance of a subtest object.

        Notes
        -----
        All parameters are mandatory.

        Parameters
        ----------
        name_of_application : str
            The name of the application.

        name_of_subtest : str
            The name of test within the application. 

        local_path_to_tests : str
            The path to to the subtest.

        logger : A rgt_logger object.
            A logger object

        db_logger : A rgt_database_logger object
            A database logger object.

        tag : str
            A string that serves as unique identifier for a subtest test iteration.

        """
        
        a_subtest = subtest(name_of_application=name_of_application,
                            name_of_subtest=name_of_subtest,
                            local_path_to_tests=local_path_to_tests,
                            logger=logger,
                            db_logger=db_logger,
                            tag=tag)
        return a_subtest

    #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
    #                                                                 @
    # End of public methods.                                          @
    #                                                                 @
    #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
