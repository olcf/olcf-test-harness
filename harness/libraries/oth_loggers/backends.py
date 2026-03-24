from abc import ABC, abstractmethod
from enum import IntEnum
from pathlib import Path
from sys import stderr
from typing import Union


class LogLevel(IntEnum):
    NOTSET = 0
    DEBUG = 10
    INFO = 20
    WARNING = 30
    ERROR = 40
    CRITICAL = 50


class OTHLogger(ABC):
    def __init__(
        self,
        name: str,
        log_file_path: Union[str, None],
        log_level: str,
        console_log_level: str,
        file_log_level: str,
    ) -> None:
        super().__init__()

        self._name: str = name
        self._log_level: str = log_level.upper()
        self._console_log_level: str = console_log_level.upper()
        self._file_log_level: str = file_log_level.upper()

        # create the log file's parent directory
        if log_file_path:
            self._log_file_path: Path = Path(log_file_path)
            self._log_file_path.parent.mkdir(parents=True, exist_ok=True)

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
    def doDebugLogging(self, message: str) -> None:
        pass

    @abstractmethod
    def doInfoLogging(self, message: str) -> None:
        pass

    @abstractmethod
    def doWarningLogging(self, message: str) -> None:
        pass

    @abstractmethod
    def doErrorLogging(self, message: str) -> None:
        pass

    @abstractmethod
    def doCriticalLogging(self, message: str) -> None:
        pass


class DefaultLogger(OTHLogger):
    def __init__(
        self,
        name: str,
        log_file_path: Union[str, None],
        log_level: str,
        console_log_level: str,
        file_log_level: str,
    ) -> None:
        super().__init__(
            name, log_file_path, log_level, console_log_level, file_log_level
        )

        import logging as py_l

        self._logger = py_l.getLogger(self._name)

        if self._logger.hasHandlers():
            self.doInfoLogging(
                "Found existing handlers for logger '{}'. The existing logger and handlers will be used without modifications."
            )
        else:
            self._logger.setLevel(self._log_level)

            # console handler
            ch = py_l.StreamHandler()
            ch.setLevel(self._console_log_level)
            self._logger.addHandler(ch)

            # file handler
            if log_file_path:
                fh = py_l.FileHandler(self._log_file_path)
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

    def doDebugLogging(self, message: str) -> None:
        self._logger.debug(message)

    def doInfoLogging(self, message: str) -> None:
        self._logger.info(message)

    def doWarningLogging(self, message: str) -> None:
        self._logger.warning(message)

    def doErrorLogging(self, message: str) -> None:
        self._logger.error(message)

    def doCriticalLogging(self, message: str) -> None:
        self._logger.critical(message)


class LoguruLogger(OTHLogger):
    # the dict[name, log_level]
    current_loggers: dict[str, str] = dict()

    def __init__(
        self,
        name: str,
        log_file_path: Union[str, None],
        log_level: str,
        console_log_level: str,
        file_log_level: str,
    ) -> None:
        super().__init__(
            name, log_file_path, log_level, console_log_level, file_log_level
        )

        from loguru import logger as lg_l

        # remove the default handler
        try:
            lg_l.remove(0)
        except ValueError:
            pass

        self._logger = lg_l.bind(name=self._name)

        if self._name in self.__class__.current_loggers:
            self.doInfoLogging(
                "Found existing handlers for logger '{}'. The existing logger and handlers will be used without modifications."
            )
            # update the current instance to keep behavior similar with the default logger
            self._log_level = self.__class__.current_loggers[self._name]
        else:
            self.__class__.current_loggers[self._name] = self._log_level

            # console handler
            self._logger.add(
                stderr,
                level=self._console_log_level,
                filter=self._should_log,
            )

            # file handler
            if log_file_path:
                self._logger.add(
                    self._log_file_path,
                    level=self._file_log_level,
                    filter=self._should_log,
                )

    def _should_log(self, record: dict) -> bool:
        if (
            record["extra"]["name"] == self._name
            and LogLevel[record["level"].name] >= LogLevel[self._log_level]
        ):
            return True
        return False

    def doDebugLogging(self, message: str) -> None:
        self._logger.opt(depth=1).debug(message)

    def doInfoLogging(self, message: str) -> None:
        self._logger.opt(depth=1).info(message)

    def doWarningLogging(self, message: str) -> None:
        self._logger.opt(depth=1).warning(message)

    def doErrorLogging(self, message: str) -> None:
        self._logger.opt(depth=1).error(message)

    def doCriticalLogging(self, message: str) -> None:
        self._logger.opt(depth=1).critical(message)
