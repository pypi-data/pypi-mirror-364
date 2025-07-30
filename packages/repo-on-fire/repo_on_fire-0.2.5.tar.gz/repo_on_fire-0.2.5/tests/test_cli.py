"""Test some aspects of the Command Line Interface."""

import pytest
from click.testing import CliRunner
from repo_on_fire.cli import cli

NATIVE_REPO_COMMANDS = [
    ("abandon", 1),
    ("branch", 1),
    ("branches", 1),
    ("checkout", 1),
    ("cherry-pick", 1),
    ("diff", 1),
    ("diffmanifests", 1),
    ("download", 1),
    ("forall", 1),
    ("grep", 1),
    ("help", 1),
    ("info", 1),
    ("list", 1),
    ("manifest", 1),
    ("overview", 1),
    ("prune", 1),
    ("rebase", 1),
    ("selfupdate", 1),
    ("smartsync", 1),
    ("stage", 1),
    ("start", 1),
    ("status", 1),
    ("sync", 1),
    ("upload", 1),
    ("version", 0),
]


@pytest.mark.parametrize("command,exit_code_on_help", NATIVE_REPO_COMMANDS)
def test_command_forwarding_to_repo(command, exit_code_on_help):
    """Test if calling native repo commands works."""
    runner = CliRunner()
    result = runner.invoke(cli, [command, "--help"])
    assert result.exit_code == exit_code_on_help
