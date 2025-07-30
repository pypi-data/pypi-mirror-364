"""Repo on fire main application."""

import json
import sys
from pathlib import Path
from typing import List, Optional

from .configuration import Configuration, get_user_config_file_path, load_configuration
from .repo import Repo
from .workspace import Workspace


class Application:
    """The repo-on-fire application."""

    def __init__(self, configuration: Optional[Configuration] = None) -> None:
        """Create a new instance of the app.

        Args:
            configuration: The configuration to use. If not given, load from
                           default settings files.
        """
        if configuration is not None:
            self._configuration = configuration
        else:
            self._configuration = load_configuration()
        self._repo = Repo(self._configuration)
        self._workspace = Workspace(self._repo)

    @property
    def workspace(self) -> Workspace:
        """Utilities to manipulate a repo workspace."""
        return self._workspace

    def run_native_repo_command(self, command: str, args: List[str], cwd: Optional[Path] = None):
        """Runs a native repo command.

        This runs the repo tool with the given command and arguments.

        Args:
            command: The command to run (e.g. init, sync, ...).
            args: A list of additional options to pass to repo.
            cwd: The directory where to run repo. If omitted, run in the current
                working directory.
        """
        additional_args = []
        if self._configuration.native_command_additional_arguments is not None:
            additional_args = self._configuration.native_command_additional_arguments.get(
                command, []
            )
        result = self._repo.call([command, *additional_args, *args], cwd=cwd)
        sys.exit(result)

    def init_workspace_from_cache(  ## noqa: PLR0913
        self,
        manifest_url: str,
        manifest_name: Optional[str],
        manifest_branch: Optional[str],
        args: List[str],
        workspace_path: Optional[Path] = None,
    ):
        """Initialize a workspace from the cache.

        This runs a "special" init command, which will create a workspace from
        a mirror workspace in the app's cache. If the mirror workspace does not
        exist, it will be created first. On top, the cache entry will be kept
        up to date by running a sync on it every time the init command is run.

        Args:
            manifest_url: The URL of the repository where the repo manifest is stored.
            manifest_name: The name of the manifest file within the repository.
            manifest_branch: The branch in the manifest repository to use.
            args: Additional arguments to be passed to the init command
                run in the target workspace.
            workspace_path: The path to where the workspace shall be created.
                If omitted, the current working directory will be used.
        """
        self._repo.create_or_update_cache_entry(manifest_url, manifest_name, manifest_branch)
        self._repo.init_from_cache_entry(
            manifest_url, manifest_name, manifest_branch, args, workspace_path=workspace_path
        )

    def show_config_file_path(self, print_as_json: bool = False):
        """Print the path to the configuration file."""
        if print_as_json:
            data = {"path": str(get_user_config_file_path())}
            print(json.dumps(data, indent="  "))
        else:
            print(get_user_config_file_path())

    def list_config(self, print_as_json: bool = False):
        """Print the configuration settings used by the app."""
        if print_as_json:
            print(self._configuration.model_dump_json(indent=2))
        else:
            config_dict = self._configuration.model_dump()
            for key, value in config_dict.items():
                print(f"{key} = {value}")
