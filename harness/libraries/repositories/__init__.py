import os
from typing import Optional

from .base import BaseRepository
from .git import GitRepository


def create_repository(
    _type: str,
    application: str,
    url: Optional[str] = None,
    branch: Optional[str] = None,
) -> BaseRepository:

    repo: Optional[BaseRepository] = None
    if _type == "git":
        repo = GitRepository(application, url, branch)
    else:
        raise TypeError(
            f"The repository type {_type} is not supported. This error is generally due to the environmental variable 'RGT_TYPE_OF_REPOSITORY' not being set correctly"
        )

    return repo


def get_type_of_repository() -> Optional[str]:
    return os.getenv("RGT_TYPE_OF_REPOSITORY")


__all__ = ["create_repository", "get_type_of_repository"]
