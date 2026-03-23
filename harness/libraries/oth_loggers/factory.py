from os import getenv

from .backends import OTHLogger, DefaultLogger, LoguruLogger


def create_oth_logger(
    name: str,
    log_file_path: str | None = None,
    log_level: str = "CRITICAL",
    console_log_level: str = "CRITICAL",
    file_log_level: str = "CRITICAL",
) -> OTHLogger:
    backend: str = getenv("OTH_LOGGER_BACKEND")
    logger: OTHLogger | None = None

    if backend == "loguru":
        try:
            logger = LoguruLogger(
                name,
                log_file_path,
                log_level,
                console_log_level,
                file_log_level,
            )
        except ModuleNotFoundError:
            logger = DefaultLogger(
                name,
                log_file_path,
                log_level,
                console_log_level,
                file_log_level,
            )
            logger.doWarningLogging(
                "The 'loguru' Python module is missing. Falling back to the default Python logger."
            )

    else:
        logger = DefaultLogger(
            name,
            log_file_path,
            log_level,
            console_log_level,
            file_log_level,
        )

    return logger
