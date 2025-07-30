"""Functionality to handle configuration of the app."""

import os
from pathlib import Path
from typing import Dict, List, Optional

import appdirs
import tomlkit
from pydantic_settings import BaseSettings, SettingsConfigDict

from .constants import (
    APP_AUTHOR,
    APP_NAME,
    CONFIG_FILE_NAME,
    CONFIG_FILE_NAME_ENV_VAR,
    WorkspaceCacheStrategy,
)


class Configuration(BaseSettings):
    """Holds configurable application settings."""

    model_config = SettingsConfigDict(env_prefix="rof_")
    """Model configuration."""

    cache_path: Path = Path(appdirs.user_cache_dir(appname=APP_NAME, appauthor=APP_AUTHOR))
    """The path to the app cache."""

    repo_url: Optional[str] = None
    """The URL to clone Google's repo tool from."""

    repo_rev: Optional[str] = None
    """The revision of Google's repo tool to use."""

    repo_script_url: str = "https://storage.googleapis.com/git-repo-downloads/repo"
    """The URL of repo's starter script."""

    workspace_cache_strategy: WorkspaceCacheStrategy = WorkspaceCacheStrategy.auto_sync
    """The strategy to use for maintaining the workspace cache."""

    http_proxy: Optional[str] = None
    """HTTP proxy to use for web requests."""

    https_proxy: Optional[str] = None
    """HTTPS proxy to use for web requests."""

    verify_https_requests: bool = True
    """If set to False, disable verification of HTTPS requests."""

    native_command_additional_arguments: Optional[Dict[str, List[str]]] = None
    """Additional arguments to pass to native repo commands.

    This map holds a list of additional arguments to be passed to native
    repo commands when invoking the.
    """


def get_user_config_file_path() -> Path:
    """Get the path to the user app configuration."""
    # Check if the user wants to force use of a specific file:
    if CONFIG_FILE_NAME_ENV_VAR in os.environ:
        return Path(os.environ[CONFIG_FILE_NAME_ENV_VAR])

    # If not, assume the file to be in the user's config dir:
    sys_conf_dir = appdirs.user_config_dir(appname=APP_NAME, appauthor=APP_AUTHOR)
    sys_conf_path = Path(sys_conf_dir)
    sys_conf_file_path = sys_conf_path / CONFIG_FILE_NAME
    return sys_conf_file_path


def load_configuration() -> Configuration:
    """Load app configuration.

    This loads the configuration of the app. Currently, this checks if a
    config file in a OS specific folder is present and tries to read the
    configuration from there. Otherwise, settings will be read from the
    environment. Finally, if neither is present, settings are taken from
    sane built-ins.
    """
    user_conf_path = get_user_config_file_path()
    if user_conf_path.exists():
        data = tomlkit.loads(user_conf_path.read_text(encoding="utf-8"))
        return Configuration(**data)
    return Configuration()
