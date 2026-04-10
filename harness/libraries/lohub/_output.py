from abc import ABC, abstractmethod
from enum import StrEnum


class OutputLevel(StrEnum):
    NOTSET = ""
    V = "v"
    VV = "vv"
    VVV = "vvv"


class Output(ABC):
    def __init__(self, *args, output_level: str = "", colorize: bool = False, **kwargs):
        super().__init__(*args, **kwargs)

        try:
            self._output_level: OutputLevel = OutputLevel(output_level)
        except ValueError:
            raise ValueError(f"'{output_level}' is not a valid output level")
        self._colorize: bool = colorize

    @property
    def output_level(self) -> str:
        return self._output_level

    @abstractmethod
    def print(self, message: str) -> None:
        pass

    @abstractmethod
    def print_v(self, message: str) -> None:
        pass

    @abstractmethod
    def print_vv(self, message: str) -> None:
        pass

    @abstractmethod
    def print_vvv(self, message: str) -> None:
        pass


class DefaultOutput(Output):
    def _colorize_message(self, message: str) -> str:
        return f"\033[1;34m{message}\033[0m" if self._colorize else message

    def print(self, message: str) -> None:
        print(self._colorize_message(message))

    def print_v(self, message: str) -> None:
        if self.output_level >= OutputLevel.V:
            print(self._colorize_message(message))

    def print_vv(self, message: str) -> None:
        if self.output_level >= OutputLevel.VV:
            print(self._colorize_message(message))

    def print_vvv(self, message: str) -> None:
        if self.output_level == OutputLevel.VVV:
            print(self._colorize_message(message))
