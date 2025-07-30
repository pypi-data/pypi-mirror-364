"""Test the application class."""

import pytest
from repo_on_fire.application import Application
from repo_on_fire.configuration import Configuration


def test_constructor():
    """Test if we can construct an application object."""
    Application(configuration=Configuration())


def test_help_repo_command():
    """Test if we can show the help for a repo command."""
    app = Application(configuration=Configuration())
    with pytest.raises(SystemExit):
        app.run_native_repo_command("sync", ["--help"])
