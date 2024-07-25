#! /usr/bin/env python3
"""
This module implements the factory class for creating rgt_loggers.
"""


from .rgt_database_logger import RgtDatabaseLogger

def create_rgt_db_logger(logger=None):
    """Creates and returns an instance of rgt_database_logger.

    Parameters
    ----------
    logger_name : str
        The name of the logger.

    Returns
    -------
    RgtDatabaseLogger
        An instance of the RgtDatabaseLogger class.
    """

    a_rgt_logger = RgtDatabaseLogger(logger=logger)
    return a_rgt_logger
