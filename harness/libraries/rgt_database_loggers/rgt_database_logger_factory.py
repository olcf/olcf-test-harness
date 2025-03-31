#! /usr/bin/env python3
"""
This module implements the factory class for creating rgt_loggers.
"""


from .rgt_database_logger import RgtDatabaseLogger

def create_rgt_db_logger(logger=None, only=None):
    """Creates and returns an instance of rgt_database_logger.

    Parameters
    ----------
    logger : rgt_logger
        The rgt_logger object for logging
    only : str
        (Optional) The URL of a single database to enable

    Returns
    -------
    RgtDatabaseLogger
        An instance of the RgtDatabaseLogger class.
    """

    a_rgt_logger = RgtDatabaseLogger(logger=logger, only=only)
    return a_rgt_logger
