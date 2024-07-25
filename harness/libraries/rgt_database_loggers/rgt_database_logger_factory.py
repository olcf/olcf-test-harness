#! /usr/bin/env python3
"""
This module implements the factory class for creating rgt_loggers.
"""


from .rgt_database_logging import RgtDatabaseLogger

def create_rgt_db_logger(logger_name=None,
                         fh_filepath=None,
                         logger_threshold_log_level=None,
                         fh_threshold_log_level=None,
                         ch_threshold_log_level=None):
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

    a_rgt_logger = RgtDatabaseLogger(logger_name=logger_name)
    return a_rgt_logger
