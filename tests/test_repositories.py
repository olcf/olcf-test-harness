import configparser
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Optional

import pytest

from harness.libraries.output_hub import OutputHub
from harness.libraries.repositories import create_repository, get_type_of_repository
from harness.libraries.repositories.base import BaseRepository
from harness.libraries.repositories.git import (
    GitCloneStatus,
    GitRepository,
    IncorrectGitRepositoryOrigin,
    InvalidGitTransferProtocol,
)

# ---------------------------------------------------------------------------
# Test BaseRepository
# ---------------------------------------------------------------------------


def test_instantiate_base_repository():
    with pytest.raises(TypeError):
        BaseRepository("pytest")

    class BadDummyRepository(BaseRepository):
        pass

    with pytest.raises(TypeError):
        BadDummyRepository("pytest")

    class GoodDummyRepository(BaseRepository):
        @classmethod
        def get_application_parent_directory_from_env(cls) -> str:
            return "apd"

        @classmethod
        def get_repository_branch_from_env(cls) -> Optional[str]:
            return "rb"

        def _build_repository_url_from_env(self) -> str:
            return "url"

        def clone(self, destination: Path, logger: OutputHub) -> None:
            pass

    with pytest.raises(TypeError):
        GoodDummyRepository()

    gd = GoodDummyRepository("pytest")
    assert gd.application == "pytest"
    assert gd.url == "url"
    assert gd.branch == "rb"


# ---------------------------------------------------------------------------
# Test GitRepository
# ---------------------------------------------------------------------------


def test_get_application_parent_directory_from_env(monkeypatch):
    with pytest.raises(ValueError):
        GitRepository.get_application_parent_directory_from_env()

    monkeypatch.setenv("RGT_GIT_SERVER_APPLICATION_PARENT_DIR", "somewhere/tests")
    assert (
        GitRepository.get_application_parent_directory_from_env() == "somewhere/tests"
    )


def test_get_repository_branch_from_env(monkeypatch):
    assert GitRepository.get_repository_branch_from_env() == None

    monkeypatch.setenv("RGT_GIT_REPS_BRANCH", "pytest")
    assert GitRepository.get_repository_branch_from_env() == "pytest"


def test_git_check_for_existing_clone():
    git_config = configparser.ConfigParser()
    git_config.read(".git/config")
    current_origin = git_config['remote "origin"']["url"]
    gr = GitRepository("pytest", url=current_origin)

    assert (
        gr._check_for_existing_clone(Path(__file__).parent.parent)
        == GitCloneStatus.CLONED_WITH_CORRECT_ORIGIN
    )

    with TemporaryDirectory() as temp_dir:
        assert gr._check_for_existing_clone(Path(temp_dir)) == GitCloneStatus.NOT_CLONED

    gr.url = "https://github.com/error/olcf-test-harness.git"
    assert (
        gr._check_for_existing_clone(Path(__file__).parent.parent)
        == GitCloneStatus.CLONED_WITH_INCORRECT_ORIGIN
    )


def test_build_repository_url_from_env(monkeypatch):
    monkeypatch.setenv("RGT_GIT_MACHINE_NAME", "machine")
    monkeypatch.setenv("RGT_GIT_SERVER_APPLICATION_PARENT_DIR", "somewhere/tests")

    monkeypatch.setenv("RGT_GIT_DATA_TRANSFER_PROTOCOL", "ssh")
    monkeypatch.setenv("RGT_GIT_SSH_SERVER_URL", "git@github.com")
    assert (
        GitRepository("pytest")._build_repository_url_from_env()
        == "git@github.com:somewhere/tests/machine/pytest.git"
    )

    monkeypatch.setenv("RGT_GIT_DATA_TRANSFER_PROTOCOL", "https")
    monkeypatch.setenv("RGT_GIT_HTTPS_SERVER_URL", "https://github.com")
    assert (
        GitRepository("pytest")._build_repository_url_from_env()
        == "https://github.com/somewhere/tests/machine/pytest.git"
    )

    monkeypatch.setenv("RGT_GIT_DATA_TRANSFER_PROTOCOL", "proto")
    with pytest.raises(InvalidGitTransferProtocol):
        GitRepository("pytest")


def test_clone():
    oh = OutputHub("pytest")
    gr = GitRepository("pytest", url="https://github.com/olcf/olcf-test-harness.git")

    with TemporaryDirectory() as temp_dir:
        td = Path(temp_dir)
        gr.clone(td, oh)
        assert td.joinpath("olcf-test-harness/README.md").exists()

        gr.clone(td, oh)

        gr.url = "https://github.com/error/olcf-test-harness.git"
        with pytest.raises(IncorrectGitRepositoryOrigin):
            gr.clone(td, oh)

    with TemporaryDirectory() as temp_dir:
        td = Path(temp_dir)
        gr.url = "https://github.com/olcf/olcf-test-harness.git"
        gr.branch = "v3.2"
        gr.clone(td, oh)
        with open(td.joinpath("olcf-test-harness/.git/HEAD")) as f:
            assert f.read() == "47dfced0bb043866e6fbb243d402ab5e3a751dbe\n"


# ---------------------------------------------------------------------------
# Test repositories module
# ---------------------------------------------------------------------------


def test_create_repository():
    with pytest.raises(TypeError):
        create_repository("error", "pytest")

    repo = create_repository("git", "pytest", url="url", branch="branch")
    assert isinstance(repo, GitRepository)
    assert repo.application == "pytest"
    assert repo.url == "url"
    assert repo.branch == "branch"


def test_get_type_of_repository(monkeypatch):
    assert get_type_of_repository() == None

    monkeypatch.setenv("RGT_TYPE_OF_REPOSITORY", "git")
    assert get_type_of_repository() == "git"
