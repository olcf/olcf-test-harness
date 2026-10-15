from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional

from harness.libraries.output_hub import OutputHub


class BaseRepository(ABC):
    executable: str = "echo"

    @classmethod
    @abstractmethod
    def get_application_parent_directory_from_env(cls) -> str:
        pass

    @classmethod
    @abstractmethod
    def get_repository_branch_from_env(cls) -> Optional[str]:
        pass

    def __init__(
        self, application: str, url: Optional[str] = None, branch: Optional[str] = None
    ):
        self.application: str = application
        self.url: str = url if url else self._build_repository_url_from_env()
        self.branch: Optional[str] = (
            branch if branch else self.get_repository_branch_from_env()
        )

    @abstractmethod
    def _build_repository_url_from_env(self) -> str:
        pass

    @abstractmethod
    def clone(self, destination: Path, logger: OutputHub) -> None:
        pass
