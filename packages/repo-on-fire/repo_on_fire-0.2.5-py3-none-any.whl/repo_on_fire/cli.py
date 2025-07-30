"""Definition of the command line interface of the application.

This module defines the available command line interface of the app. Most
of the concrete commands are simple wrappers around the native repo commands.
However, repo-on-fire also has some own ones. Additionally, the tool decorates
some of repo's built in commands, adding some functionality on top.
"""

from typing import List, Optional

import click

from repo_on_fire.exceptions import RepoOnFireException

from .application import Application


@click.group("Repo on Fire Commands")
def cli():
    """This tool is a wrapper around the repo command line tool.

    It allows calling any repo command as usual. On top, some repo-on-fire
    specific commands are added on top.
    """


################################################################################
# Native Repo Commands
################################################################################


@cli.command(add_help_option=False, context_settings={"ignore_unknown_options": True})
@click.argument("args", nargs=-1, type=click.UNPROCESSED)
def abandon(args: List[str]):
    """Permanently abandon a development branch."""
    app = Application()
    app.run_native_repo_command("abandon", args)


@cli.command(add_help_option=False, context_settings={"ignore_unknown_options": True})
@click.argument("args", nargs=-1, type=click.UNPROCESSED)
def branch(args: List[str]):
    """View current topic branches."""
    app = Application()
    app.run_native_repo_command("branch", args)


@cli.command(add_help_option=False, context_settings={"ignore_unknown_options": True})
@click.argument("args", nargs=-1, type=click.UNPROCESSED)
def branches(args: List[str]):
    """View current topic branches."""
    app = Application()
    app.run_native_repo_command("branches", args)


@cli.command(add_help_option=False, context_settings={"ignore_unknown_options": True})
@click.argument("args", nargs=-1, type=click.UNPROCESSED)
def checkout(args: List[str]):
    """Checkout a branch for development."""
    app = Application()
    app.run_native_repo_command("checkout", args)


@cli.command(add_help_option=False, context_settings={"ignore_unknown_options": True})
@click.argument("args", nargs=-1, type=click.UNPROCESSED)
def cherry_pick(args: List[str]):
    """Cherry-pick a change.."""
    app = Application()
    app.run_native_repo_command("cherry-pick", args)


@cli.command(add_help_option=False, context_settings={"ignore_unknown_options": True})
@click.argument("args", nargs=-1, type=click.UNPROCESSED)
def diff(args: List[str]):
    """Show changes between commit and working tree."""
    app = Application()
    app.run_native_repo_command("diff", args)


@cli.command(add_help_option=False, context_settings={"ignore_unknown_options": True})
@click.argument("args", nargs=-1, type=click.UNPROCESSED)
def diffmanifests(args: List[str]):
    """Manifest diff utility."""
    app = Application()
    app.run_native_repo_command("diffmanifests", args)


@cli.command(add_help_option=False, context_settings={"ignore_unknown_options": True})
@click.argument("args", nargs=-1, type=click.UNPROCESSED)
def download(args: List[str]):
    """Download and checkout a change."""
    app = Application()
    app.run_native_repo_command("download", args)


@cli.command(add_help_option=False, context_settings={"ignore_unknown_options": True})
@click.argument("args", nargs=-1, type=click.UNPROCESSED)
def forall(args: List[str]):
    """Run a shell command in each project."""
    app = Application()
    app.run_native_repo_command("forall", args)


@cli.command(add_help_option=False, context_settings={"ignore_unknown_options": True})
@click.argument("args", nargs=-1, type=click.UNPROCESSED)
def grep(args: List[str]):
    """Print lines matching a pattern."""
    app = Application()
    app.run_native_repo_command("grep", args)


@cli.command(add_help_option=False, context_settings={"ignore_unknown_options": True})
@click.argument("args", nargs=-1, type=click.UNPROCESSED)
def help(args: List[str]):
    """Display detailed help on a command."""
    app = Application()
    app.run_native_repo_command("help", args)


@cli.command(add_help_option=False, context_settings={"ignore_unknown_options": True})
@click.argument("args", nargs=-1, type=click.UNPROCESSED)
def info(args: List[str]):
    """Get info on the manifest branch, current branch or unmerged branches."""
    app = Application()
    app.run_native_repo_command("info", args)


@cli.command(add_help_option=False, context_settings={"ignore_unknown_options": True})
@click.argument("args", nargs=-1, type=click.UNPROCESSED)
def list(args: List[str]):
    """List projects and their associated directories."""
    app = Application()
    app.run_native_repo_command("list", args)


@cli.command(add_help_option=False, context_settings={"ignore_unknown_options": True})
@click.argument("args", nargs=-1, type=click.UNPROCESSED)
def manifest(args: List[str]):
    """Manifest inspection utility."""
    app = Application()
    app.run_native_repo_command("manifest", args)


@cli.command(add_help_option=False, context_settings={"ignore_unknown_options": True})
@click.argument("args", nargs=-1, type=click.UNPROCESSED)
def overview(args: List[str]):
    """Display overview of unmerged project branches."""
    app = Application()
    app.run_native_repo_command("overview", args)


@cli.command(add_help_option=False, context_settings={"ignore_unknown_options": True})
@click.argument("args", nargs=-1, type=click.UNPROCESSED)
def prune(args: List[str]):
    """Prune (delete) already merged topics."""
    app = Application()
    app.run_native_repo_command("prune", args)


@cli.command(add_help_option=False, context_settings={"ignore_unknown_options": True})
@click.argument("args", nargs=-1, type=click.UNPROCESSED)
def rebase(args: List[str]):
    """Rebase local branches on upstream branch."""
    app = Application()
    app.run_native_repo_command("rebase", args)


@cli.command(add_help_option=False, context_settings={"ignore_unknown_options": True})
@click.argument("args", nargs=-1, type=click.UNPROCESSED)
def selfupdate(args: List[str]):
    """Update repo to the latest version."""
    app = Application()
    app.run_native_repo_command("selfupdate", args)


@cli.command(add_help_option=False, context_settings={"ignore_unknown_options": True})
@click.argument("args", nargs=-1, type=click.UNPROCESSED)
def smartsync(args: List[str]):
    """Update working tree to the latest known good revision."""
    app = Application()
    app.run_native_repo_command("smartsync", args)


@cli.command(add_help_option=False, context_settings={"ignore_unknown_options": True})
@click.argument("args", nargs=-1, type=click.UNPROCESSED)
def stage(args: List[str]):
    """Stage file(s) for commit."""
    app = Application()
    app.run_native_repo_command("stage", args)


@cli.command(add_help_option=False, context_settings={"ignore_unknown_options": True})
@click.argument("args", nargs=-1, type=click.UNPROCESSED)
def start(args: List[str]):
    """Start a new branch for development."""
    app = Application()
    app.run_native_repo_command("start", args)


@cli.command(add_help_option=False, context_settings={"ignore_unknown_options": True})
@click.argument("args", nargs=-1, type=click.UNPROCESSED)
def status(args: List[str]):
    """Show the working tree status."""
    app = Application()
    app.run_native_repo_command("status", args)


@cli.command(add_help_option=False, context_settings={"ignore_unknown_options": True})
@click.argument("args", nargs=-1, type=click.UNPROCESSED)
def sync(args: List[str]):
    """Update working tree to the latest revision."""
    app = Application()
    app.run_native_repo_command("sync", args)


@cli.command(add_help_option=False, context_settings={"ignore_unknown_options": True})
@click.argument("args", nargs=-1, type=click.UNPROCESSED)
def upload(args: List[str]):
    """Upload changes for code review."""
    app = Application()
    app.run_native_repo_command("upload", args)


@cli.command(add_help_option=False, context_settings={"ignore_unknown_options": True})
@click.argument("args", nargs=-1, type=click.UNPROCESSED)
def version(args: List[str]):
    """Display the version of repo."""
    app = Application()
    app.run_native_repo_command("version", args)


################################################################################
# Decorated Repo Commands
################################################################################


@cli.command(add_help_option=False, context_settings={"ignore_unknown_options": True})
@click.argument("args", nargs=-1, type=click.UNPROCESSED)
@click.option("-u", "--manifest-url", type=str)
@click.option("-m", "--manifest-name", type=str)
@click.option("-b", "--manifest-branch", type=str)
@click.option("--mirror", is_flag=True)
@click.option("--reference", is_flag=True)
@click.option("--help", is_flag=True)
def init(  # noqa: PLR0913
    args: List[str],
    manifest_url: Optional[str],
    manifest_name: Optional[str],
    manifest_branch: Optional[str],
    mirror: bool,
    reference: bool,
    help: bool,
):
    """Initialize a repo client checkout in the current directory."""
    app = Application()
    if mirror or reference or help:
        # User used mirror or reference manually - assume they want to do some
        # manual caching, so better get out of their way and just call the
        # basic init command as is. Same applies if the help option is used.
        if manifest_url is not None:
            args += ("-u", manifest_url)
        if manifest_name is not None:
            args += ("-m", manifest_name)
        if manifest_branch is not None:
            args += ["-b", manifest_branch]
        if mirror:
            args += ("--mirror",)
        if reference:
            args += ("--reference",)
        if help:
            args += ("--help",)
        app.run_native_repo_command("init", args)
    else:
        if manifest_url is None:
            raise RepoOnFireException("Missing repository URL")
        app.init_workspace_from_cache(
            manifest_url=manifest_url,
            manifest_name=manifest_name,
            manifest_branch=manifest_branch,
            args=args,
        )


################################################################################
# Native repo-on-fire Commands
################################################################################


@cli.group()
def workspace():
    """Workspace manipulation commands."""


@workspace.command(name="switch")
@click.argument("branch", type=str)
def workspace_switch(branch: str):
    """Switch the workspace to a different branch.

    This will first run a sync on the workspace, detaching any potentially
    checked out branches. Afterwards, an attempt is made to check out the
    given branch in all repositories in the workspace.

    If the branch can be checked out in at least one repository, the call
    succeeds, otherwise, the command exits with an error.
    """
    app = Application()
    app.workspace.switch(branch)


@cli.group()
def config():
    """Configuration of the tool."""


@config.command(name="path")
@click.option("--json", is_flag=True, help="Print as JSON.")
def config_path(json: bool):
    """Print the path to the user configuration file."""
    Application().show_config_file_path(print_as_json=json)


@config.command(name="list")
@click.option("--json", is_flag=True, help="Print as JSON.")
def config_list(json: bool):
    """Print the current configuration."""
    Application().list_config(print_as_json=json)
