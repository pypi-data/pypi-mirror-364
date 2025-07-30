"""Workspace Utilities."""

import shlex
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

from .exceptions import RepoOnFireException
from .repo import Repo

HELPER_SCRIPT_PATH = Path(__file__).parent / "_workspace_helper.py"


class Workspace:
    """Interact with a repo workspace.

    This class provides some high level utilities that can be used to efficiently
    modify a repo workspace. It does not reinvent the wheel but instead delegates
    a lot of work to repo, encapsulating stuff here and there to make things easy.
    """

    def __init__(self, repo: Repo):
        """Initialize a new Workspace instance.

        Args:
            repo: The Repo instance used by the workspace.
        """
        self._repo = repo

    def switch(self, branch: str):
        """Switch a workspace to a specific branch.

        This method will try to switch the workspace to a particular branch.
        First, it calls `repo sync -d` to bring the workspace up to date and
        switch away from any already checked out branch. Then, it will use
        a `repo forall` command which tries to check out the given branch in any
        project in the workspace.

        If checking out the branch fails for all projects, the method raises
        a RepoOnFireException exception.

        Args:
            branch: The branch to checkout.

        Raises:
            RepoOnFireException: In case either the sync fails or the desired
                branch cannot be checked out in any repository.
        """
        result = self._repo.call(["sync", "-d"])
        if result != 0:
            raise RepoOnFireException("Failed to detach workspace to defaults")
        with TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            stamp_file = temp_path / "success.txt"
            inner_args = [
                sys.executable,
                str(HELPER_SCRIPT_PATH),
                "checkout",
                branch,
                str(stamp_file),
            ]
            result = self._repo.call(["forall", "-c", shlex.join(inner_args)])
            if result != 0:
                raise RepoOnFireException(f"Failed to checkout branch {branch} in workspace")
            if not stamp_file.exists():
                raise RepoOnFireException(f"Failed to checkout {branch} in any project")
