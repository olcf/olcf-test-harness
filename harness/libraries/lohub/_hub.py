from abc import ABCMeta

from ._logging import Logger, DefaultLogger
from ._output import Output, DefaultOutput


class LOHubMeta(ABCMeta):
    def __new__(mcs, name, bases, namespace):
        # This is where we would replace the default bases
        new_bases: tuple[type[Logger], type[Output]] = (DefaultLogger, DefaultOutput)
        return super().__new__(mcs, name, new_bases, namespace)


class LOHub(DefaultLogger, DefaultOutput, metaclass=LOHubMeta):
    """Logging and Output hub."""
