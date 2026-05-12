from abc import ABC, abstractmethod
from enum import IntEnum
from pathlib import Path
from typing import Optional


class LogLevel(IntEnum):
    NOTSET = 0
    DEBUG = 10
    INFO = 20
    WARNING = 30
    ERROR = 40
    CRITICAL = 50


class Logger(ABC):
    def __init__(
        self,
        name: str,
        *args,
        log_file: Optional[str] = None,
        log_level: str = "WARNING",
        console_log_level: str = "WARNING",
        file_log_level: str = "WARNING",
        **kwargs,
    ):
        super().__init__(*args, **kwargs)

        self._name: str = name
        try:
            self._log_level: LogLevel = getattr(LogLevel, log_level.upper())
            self._console_log_level: LogLevel = getattr(
                LogLevel, console_log_level.upper()
            )
            self._file_log_level: LogLevel = getattr(LogLevel, file_log_level.upper())
        except AttributeError:
            raise ValueError(
                "one of'({}, {}, {})' is not a valid log level".format(
                    log_level, console_log_level, file_log_level
                )
            )

        # create the log file's parent directory
        if log_file:
            self._log_file: Path = Path(log_file)
            self._log_file.parent.mkdir(parents=True, exist_ok=True)
        else:
            self._log_file = None

        self._setup_handlers()

    @abstractmethod
    def _setup_handlers(self) -> None:
        pass

    @property
    def log_level(self) -> str:
        return self._log_level

    @property
    def console_log_level(self) -> str:
        return self._console_log_level

    @property
    def file_log_level(self) -> str:
        return self._file_log_level

    @abstractmethod
    def log_debug(self, message: str) -> None:
        pass

    @abstractmethod
    def log_info(self, message: str) -> None:
        pass

    @abstractmethod
    def log_warning(self, message: str) -> None:
        pass

    @abstractmethod
    def log_error(self, message: str) -> None:
        pass

    @abstractmethod
    def log_critical(self, message: str) -> None:
        pass


class DefaultLogger(Logger):
    def _setup_handlers(self) -> None:
        import logging as py_l

        self._logger = py_l.getLogger(self._name)

        if self._logger.hasHandlers():
            self.log_info(
                "Found existing handlers for logger '{}'. The existing logger and handlers will be used without modifications."
            )
        else:
            self._logger.setLevel(self._log_level)

            # console handler
            ch = py_l.StreamHandler()
            ch.setLevel(self._console_log_level)
            self._logger.addHandler(ch)

            # file handler
            if self._log_file:
                fh = py_l.FileHandler(self._log_file)
                fh.setLevel(self._file_log_level)
                fh_fmt_str = "-----\n"
                fh_fmt_str += "Time: %(asctime)s\n"
                fh_fmt_str += "Logger: %(name)s\n"
                fh_fmt_str += "Loglevel: %(levelname)s\n"
                fh_fmt_str += "Message:\n"
                fh_fmt_str += "%(message)s\n"
                fh_fmt_str += "-----\n"
                fh_fmt = py_l.Formatter(fh_fmt_str)
                fh.setFormatter(fh_fmt)
                self._logger.addHandler(fh)

    def log_debug(self, message: str) -> None:
        self._logger.debug(message)

    def log_info(self, message: str) -> None:
        self._logger.info(message)

    def log_warning(self, message: str) -> None:
        self._logger.warning(message)

    def log_error(self, message: str) -> None:
        self._logger.error(message)

    def log_critical(self, message: str) -> None:
        self._logger.critical(message)
