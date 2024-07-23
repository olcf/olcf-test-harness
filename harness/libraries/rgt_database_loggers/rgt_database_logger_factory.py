#! /usr/bin/env python3
"""
This module implements the factory class for creating rgt_loggers.
"""


from .rgt_database_logging import rgt_database_logger

def create_rgt_db_logger(logger_name=None,
                         fh_filepath=None,
                         logger_threshold_log_level=None,
                         fh_threshold_log_level=None,
                         ch_threshold_log_level=None):
    """Creates and returns an instance of rgt_logger.

    Parameters
    ----------
    logger_name : str
        The name of the logger.

    fh_filepath : str
        The fully qualified file path for the logger file handler.

    logger_threshold_log_level : str
        The logging threshold level.

    fh_threshold_log_level : str
        The file handler logging threshold log level.

    ch_threshold_log_level : str
        The console file handler threshold log level.

    Returns
    -------
    rgt_logger
        An instance of the rgt_logger.
    """

    a_rgt_logger = rgt_logger(logger_name=logger_name,
                              fh_filepath=fh_filepath,
                              logger_threshold_log_level=logger_threshold_log_level,
                              fh_threshold_log_level=fh_threshold_log_level,
                              ch_threshold_log_level=ch_threshold_log_level)
    return a_rgt_logger
