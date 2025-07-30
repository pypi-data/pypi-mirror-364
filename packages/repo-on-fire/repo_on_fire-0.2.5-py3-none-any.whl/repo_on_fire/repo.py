"""Wrapper around the Google repo tool."""

import os
import os.path
import shutil
import sys
import time
from hashlib import sha256
from pathlib import Path
from subprocess import call
from tempfile import TemporaryDirectory
from typing import Any, Dict, List, NamedTuple, Optional, Tuple

import requests

from ._locks import lock_path
from .configuration import Configuration
from .constants import CACHE_ENTRY_STAMP_FILE, WorkspaceCacheStrategy
from .exceptions import RepoOnFireException


class RepoCommand(NamedTuple):
    """Holds information about a single known sub-command of the repo tool."""

    command: str
    description: str


class Repo:
    """Utility class to work with the repo command line tool."""

    def __init__(self, configuration: Configuration):
        """Create a Repo command line tool wrapper."""
        self._configuration = configuration

    def get_repo_path(self) -> Path:
        """Get the path to the local repo script."""
        return self._configuration.cache_path / "repo"

    def get_workspace_cache_entry(
        self, url: str, manifest: Optional[str] = None, branch: Optional[str] = None
    ) -> Path:
        """Get the path to a cache entry for a particular workspace.

        Given the URL and optional manifest and groups for a workspace to be
        initialized, return the path to the mirror within the cache on disk.
        """
        cache_id = self._calc_hash_id(url, manifest=manifest, branch=branch)
        return self._configuration.cache_path / "workspaces" / cache_id[0] / cache_id[1]

    def get_known_repo_commands(self) -> List[RepoCommand]:
        """Get a list of known repo commands.

        This returns a list with all the commands that we know repo implements.
        """
        return [
            RepoCommand("abandon", "Permanently abandon a development branch"),
            RepoCommand("branch", "View current topic branches"),
            RepoCommand("branches", "View current topic branches"),
            RepoCommand("checkout", "Checkout a branch for development"),
            RepoCommand("cherry-pick", "Cherry-pick a change."),
            RepoCommand("diff", "Show changes between commit and working tree"),
            RepoCommand("diffmanifests", "Manifest diff utility"),
            RepoCommand("download", "Download and checkout a change"),
            RepoCommand("forall", "Run a shell command in each project"),
            RepoCommand("grep", "Print lines matching a pattern"),
            RepoCommand("help", "Display detailed help on a command"),
            RepoCommand(
                "info", "Get info on the manifest branch, current branch or unmerged branches"
            ),
            RepoCommand("init", "Initialize a repo client checkout in the current directory"),
            RepoCommand("list", "List projects and their associated directories"),
            RepoCommand("manifest", "Manifest inspection utility"),
            RepoCommand("overview", "Display overview of unmerged project branches"),
            RepoCommand("prune", "Prune (delete) already merged topics"),
            RepoCommand("rebase", "Rebase local branches on upstream branch"),
            RepoCommand("selfupdate", "Update repo to the latest version"),
            RepoCommand("smartsync", "Update working tree to the latest known good revision"),
            RepoCommand("stage", "Stage file(s) for commit"),
            RepoCommand("start", "Start a new branch for development"),
            RepoCommand("status", "Show the working tree status"),
            RepoCommand("sync", "Update working tree to the latest revision"),
            RepoCommand("upload", "Upload changes for code review"),
            RepoCommand("version", "Display the version of repo"),
        ]

    def call(
        self, args: List[str], cwd: Optional[Path] = None, env: Optional[Dict[str, Any]] = None
    ):
        """Call the repo tool.

        This calls the repo tool that we maintain locally.

        Args:
            args: A list of arguments to pass to the repo tool.
            cwd: The current working directory to run the command in.
            env: A dictionary with environment variables to set for the command.

        Note:
            The ensure_repo() method must be called before this to ensure that
            a local clone of the repo tool is present and up to date.
        """
        self._ensure_repo()
        repo_path = self.get_repo_path()
        call_args: Dict[str, Any] = {"args": [sys.executable, str(repo_path), *args]}
        if env is not None:
            call_args["env"] = env
        if cwd is not None:
            call_args["cwd"] = str(cwd)
        return call(**call_args)

    def create_or_update_cache_entry(
        self, url: str, manifest: Optional[str] = None, branch: Optional[str] = None
    ):
        """Create or update an entry in the cache.

        This creates or keeps up to date an entry in the cache.

        Args:
            url: The URL of the repo holding the manifest.
            manifest: The path to the manifest file within the manifest repo.
            branch: The branch in the manifest repo to check out.
        """
        self._ensure_repo()
        mirror_path = self.get_workspace_cache_entry(url, manifest=manifest, branch=branch)
        with lock_path(mirror_path):
            mirror_path.mkdir(parents=True, exist_ok=True)
            stamp_file = mirror_path / CACHE_ENTRY_STAMP_FILE
            if not stamp_file.exists():
                # If there already are entries in the folder but the stamp file
                # is not there, something went wrong during initialization.
                # Clean the folder so we can properly retry:
                print(f"🧹 Removing stale cache entry {mirror_path}")
                shutil.rmtree(mirror_path, ignore_errors=True)
                mirror_path.mkdir(parents=True, exist_ok=True)

                # Initialize a (mirror) workspace here:
                print(f"🆕 Initializing mirror workspace in {mirror_path}")
                args = ["init", "-u", url]
                if manifest is not None:
                    args += ["-m", manifest]
                if branch is not None:
                    args += ["-b", branch]
                args += ["--mirror"]
                exit_code = self.call(
                    args, cwd=mirror_path, env={**os.environ, **self._get_env_repo_init()}
                )
                if exit_code != 0:
                    raise RepoOnFireException(
                        f"Failed to initialize mirror repository in {mirror_path}"
                    )
                # Update the stamp file:
                stamp_file.touch()

            # "Sync" the repo in the cache:
            print(f"⬇️ Synchronizing mirror workspace in {mirror_path}")
            exit_code = self.call(["sync"], cwd=mirror_path)
            if exit_code != 0:
                raise RepoOnFireException(f"Failed to sync the mirror repository in {mirror_path}")

    def init_from_cache_entry(  # noqa: PLR0913
        self,
        url: str,
        manifest: Optional[str] = None,
        branch: Optional[str] = None,
        args: Optional[List[str]] = None,
        workspace_path: Optional[Path] = None,
    ):
        """Initialize a workspace from a cache entry.

        This method will initialize a workspace in the current working directory.
        The workspace will be initialized from a workspace in the cache, hence,
        speeding up download times compared to a "normal" init/sync.

        If desired, the workspace_path can be set to run this in a specific
        directory.
        """
        if args is None:
            args = []
        self._ensure_repo()
        mirror_path = self.get_workspace_cache_entry(url, manifest=manifest, branch=branch)
        if workspace_path is None:
            workspace_path = Path(os.getcwd())
        print(f"⏩ Initializing workspace in {workspace_path} from {mirror_path}")
        command = ["init", "-u", url]
        if manifest is not None:
            command += ["-m", manifest]
        if branch is not None:
            command += ["-b", branch]
        command += args
        command += [f"--reference={mirror_path}"]
        if (
            self._configuration.workspace_cache_strategy
            == WorkspaceCacheStrategy.auto_sync_dissociate
        ):
            command += ["--dissociate"]
        exit_code = self.call(
            command, cwd=workspace_path, env={**os.environ, **self._get_env_repo_init()}
        )
        if exit_code != 0:
            raise RepoOnFireException(
                f"Failed to init workspace in {workspace_path} from mirror {mirror_path}"
            )

    @staticmethod
    def _calc_hash_id(url: str, manifest: Optional[str], branch: Optional[str]) -> Tuple[str, str]:
        hash_str = f"{url}-{manifest}-{branch}"
        hash = sha256(hash_str.encode()).hexdigest()
        return hash[0:2], hash

    def _ensure_repo(self):
        """Ensure repo is locally available and up to date."""
        repo_path = self.get_repo_path()

        with lock_path(repo_path):
            repo_path.parent.mkdir(parents=True, exist_ok=True)

            fetch = False

            if not repo_path.exists():
                fetch = True
            else:
                mod_time = os.path.getmtime(repo_path)
                current_time = time.time()
                age_in_seconds = current_time - mod_time
                if age_in_seconds > 60 * 60 * 24:
                    # Check for updates once a day:
                    fetch = True

            if fetch:
                self._download_repo_script(self._configuration.repo_script_url, repo_path)

    def _download_repo_script(self, url, output_path: Path):
        print(f"⬇️ Downloading repo script from {url}")
        with TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            tmp_file_path = tmp_path / output_path.name
            response = requests.get(
                url, proxies=self._get_proxies(), verify=self._configuration.verify_https_requests
            )
            if response.ok:
                tmp_file_path.write_bytes(response.content)
                shutil.move(str(tmp_file_path), str(output_path))
            else:
                raise RepoOnFireException(
                    f"Failed to download repo wrapper script: {response.reason}"
                )

    def _get_proxies(self):
        proxies = {}

        # Initialize proxies with values from environment:
        if "http_proxy" in os.environ:
            proxies["http"] = os.environ.get("http_proxy")
        if "https_proxy" in os.environ:
            proxies["https"] = os.environ.get("https_proxy")

        # If present in config, override:
        if self._configuration.http_proxy is not None:
            proxies["http"] = self._configuration.http_proxy
        if self._configuration.https_proxy is not None:
            proxies["https"] = self._configuration.https_proxy

        return proxies

    def _get_env_repo_init(self) -> Dict[str, str]:
        """Collect the environment variables to use for repo init."""
        env: Dict[str, str] = {}

        if "REPO_URL" in os.environ:
            env["REPO_URL"] = os.environ["REPO_URL"]

        if "REPO_REV" in os.environ:
            env["REPO_REV"] = os.environ["REPO_REV"]

        if self._configuration.repo_url is not None:
            env["REPO_URL"] = self._configuration.repo_url

        if self._configuration.repo_rev is not None:
            env["REPO_REV"] = self._configuration.repo_rev

        return env
