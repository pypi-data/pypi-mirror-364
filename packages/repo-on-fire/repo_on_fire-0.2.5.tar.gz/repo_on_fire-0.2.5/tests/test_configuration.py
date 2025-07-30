"""Test the configuration module."""

import os
from pathlib import Path
from tempfile import TemporaryDirectory

from repo_on_fire.configuration import Configuration, load_configuration
from repo_on_fire.constants import CONFIG_FILE_NAME_ENV_VAR

SAMPLE_CONFIG_FILE = """
repo_url = "http://example.com"
cache_path = "/tmp/foo"
"""


def test_configuration_constructor():
    """Test if we can create a Configuration object."""
    config = Configuration()
    assert config is not None


def test_config_file():
    """Test if settings can be read from a user config file."""
    with TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)
        config_path = tmp_path / "config.toml"
        config_path.write_text(SAMPLE_CONFIG_FILE)
        os.environ[CONFIG_FILE_NAME_ENV_VAR] = str(config_path)

        cfg = load_configuration()
        assert cfg.repo_url == "http://example.com"
        assert cfg.cache_path == Path("/tmp/foo")
