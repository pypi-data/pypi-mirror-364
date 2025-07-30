"""Test the repo wrapper."""

from pathlib import Path

import pytest
from repo_on_fire.configuration import Configuration
from repo_on_fire.repo import Repo

SAMPLE_URL = "https://gitlab.com/rpdev/gitreposampleproject/manifest.git"


def test_repo(tmp_path: Path):
    """Check that the simple repo wrapper works.

    We expect it to let us fetch repo and call it easily on the command line.
    """
    configuration = Configuration(cache_path=tmp_path)
    repo = Repo(configuration=configuration)
    repo.call(["init", "--help"])
    repo.call(["--help"])


def test_sync_cache(tmp_path: Path):
    """Check if workspace caching works."""
    cache_path = tmp_path / "cache"
    workspace_1 = tmp_path / "ws1"
    workspace_2 = tmp_path / "ws2"

    configuration = Configuration(cache_path=cache_path)
    repo = Repo(configuration=configuration)

    workspace_1.mkdir(parents=True)
    workspace_2.mkdir(parents=True)

    repo.create_or_update_cache_entry(SAMPLE_URL)

    repo.init_from_cache_entry(SAMPLE_URL, workspace_path=workspace_1)
    assert repo.call(["sync"], cwd=workspace_1) == 0
    assert (workspace_1 / "app" / "README.md").exists()
    assert (workspace_1 / "lib" / "README.md").exists()

    repo.init_from_cache_entry(SAMPLE_URL, workspace_path=workspace_2)
    assert repo.call(["sync"], cwd=workspace_2) == 0
    assert (workspace_2 / "app" / "README.md").exists()
    assert (workspace_2 / "lib" / "README.md").exists()


def test_repo_branch_included_in_cache(tmp_path: Path):
    """Check if workspace caching works."""
    cache_path = tmp_path / "cache"
    workspace_1 = tmp_path / "ws"

    configuration = Configuration(cache_path=cache_path)
    repo = Repo(configuration=configuration)

    workspace_1.mkdir(parents=True)

    repo.create_or_update_cache_entry(SAMPLE_URL)

    repo.init_from_cache_entry(SAMPLE_URL, workspace_path=workspace_1, branch="feature")
    assert repo.call(["sync"], cwd=workspace_1) == 0
    assert (workspace_1 / "app" / "README.md").exists()
    assert (workspace_1 / "lib" / "README.md").exists()


@pytest.mark.xfail
def test_sync_cache_dissociate(tmp_path: Path):
    """Check if the dissociate option works."""
    cache_path = tmp_path / "cache"
    workspace_1 = tmp_path / "ws1"
    workspace_2 = tmp_path / "ws2"

    configuration = Configuration(cache_path=cache_path)
    repo = Repo(configuration=configuration)

    workspace_1.mkdir(parents=True)
    workspace_2.mkdir(parents=True)

    repo.create_or_update_cache_entry(SAMPLE_URL)

    repo.init_from_cache_entry(SAMPLE_URL, workspace_path=workspace_1, args=["--dissociate"])
    assert repo.call(["sync"], cwd=workspace_1) == 0
    assert (workspace_1 / "app" / "README.md").exists()
    assert (workspace_1 / "lib" / "README.md").exists()

    repo.init_from_cache_entry(SAMPLE_URL, workspace_path=workspace_2, args=["--dissociate"])
    assert repo.call(["sync"], cwd=workspace_2) == 0
    assert (workspace_2 / "app" / "README.md").exists()
    assert (workspace_2 / "lib" / "README.md").exists()
