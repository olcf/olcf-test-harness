import os
import subprocess as sp
from enum import IntEnum
from pathlib import Path
from typing import List, Optional
from urllib.parse import urlparse

from harness.libraries.output_hub import logger

from .base import BaseRepository


class IncorrectGitRepositoryOrigin(Exception):
    pass


class InvalidGitTransferProtocol(Exception):
    def __init__(self, protocol: str):
        super().__init__(f"{protocol} is not a valid Git transfer protocol")


class GitCloneStatus(IntEnum):
    NOT_CLONED = 0
    CLONED_WITH_CORRECT_ORIGIN = 1
    CLONED_WITH_INCORRECT_ORIGIN = 2


class GitRepository(BaseRepository):
    executable: str = "git"

    @classmethod
    def get_application_parent_directory_from_env(cls) -> str:
        apd = os.getenv("RGT_GIT_SERVER_APPLICATION_PARENT_DIR")
        if not apd:
            raise ValueError(
                "variable RGT_GIT_SERVER_APPLICATION_PARENT_DIR is not set"
            )
        return str(apd)

    @classmethod
    def get_repository_branch_from_env(cls) -> Optional[str]:
        return os.getenv("RGT_GIT_REPS_BRANCH")

    def _check_for_existing_clone(self, path: Path) -> GitCloneStatus:
        repo_status: GitCloneStatus = GitCloneStatus.NOT_CLONED

        status_result: sp.CompletedProcess = sp.run(
            [self.executable, "-C", str(path), "status"], check=False
        )
        if status_result.returncode == 0:
            repo_origin: str = (
                sp.check_output(
                    [
                        self.executable,
                        "-C",
                        str(path),
                        "config",
                        "--get",
                        "remote.origin.url",
                    ]
                )
                .decode("utf-8")
                .strip()
            )
            if repo_origin == self.url:
                repo_status = GitCloneStatus.CLONED_WITH_CORRECT_ORIGIN
            else:
                repo_status = GitCloneStatus.CLONED_WITH_INCORRECT_ORIGIN

        return repo_status

    def _build_repository_url_from_env(self) -> str:
        machine_name: str = str(os.getenv("RGT_GIT_MACHINE_NAME"))
        parent_dir: str = (
            self.get_application_parent_directory_from_env() + "/" + machine_name
        )

        data_transfer_protocol: str = str(os.getenv("RGT_GIT_DATA_TRANSFER_PROTOCOL"))

        app_url: str = ""
        if data_transfer_protocol == "ssh":
            app_url = "{}:{}/{}.git".format(
                os.getenv("RGT_GIT_SSH_SERVER_URL"),
                parent_dir,
                self.application,
            )
        elif data_transfer_protocol == "https":
            app_url = "{}/{}/{}.git".format(
                os.getenv("RGT_GIT_HTTPS_SERVER_URL"),
                parent_dir,
                self.application,
            )
        else:
            raise InvalidGitTransferProtocol(data_transfer_protocol)

        return app_url

    def clone(self, destination_directory: Path) -> None:
        clone_cmd: List[str] = [self.executable, "clone"]

        if self.branch:
            clone_cmd.extend(["--branch", self.branch])

        clone_cmd.append("--recurse-submodules")
        clone_cmd.append(self.url)

        clone_path: Path = destination_directory.joinpath(
            Path(urlparse(self.url).path).stem
        )
        clone_cmd.append(str(clone_path.absolute()))

        repo_status: GitCloneStatus = self._check_for_existing_clone(clone_path)

        if repo_status == GitCloneStatus.NOT_CLONED:
            clone_path.mkdir(parents=True)
            sp.run(clone_cmd, check=True)
        elif repo_status == GitCloneStatus.CLONED_WITH_CORRECT_ORIGIN:
            logger.log_info(
                f"The directory {clone_path} exists and is already cloned. Therefore we will will skip cloning repository {self.url}."
            )
        elif repo_status == GitCloneStatus.CLONED_WITH_INCORRECT_ORIGIN:
            raise IncorrectGitRepositoryOrigin(
                f"The directory {clone_path} is an existing git repository whose origin is not {self.url}."
            )
