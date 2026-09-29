from abc import ABCMeta

from ._logging import DefaultLogger, Logger
from ._printing import DefaultPrinter, Printer


class OutputHubMeta(ABCMeta):
    def __new__(mcs, name, bases, namespace):
        # This is where we would replace the default bases
        new_bases: tuple[type[Logger], type[Printer]] = (DefaultLogger, DefaultPrinter)
        return super().__new__(mcs, name, new_bases, namespace)


class OutputHub(DefaultLogger, DefaultPrinter, metaclass=OutputHubMeta):
    """Output hub for logging and printing."""
