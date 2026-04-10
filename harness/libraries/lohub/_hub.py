from abc import ABCMeta

from ._logging import DefaultLogger
from ._output import DefaultOutput


class LOHubMeta(ABCMeta):
    def __new__(mcs, name, bases, namespace):
        # This is where we would replace the default bases
        return super().__new__(mcs, name, bases, namespace)


class LOHub(DefaultLogger, DefaultOutput, metaclass=LOHubMeta):
    pass
