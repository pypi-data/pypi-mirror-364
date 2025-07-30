"""Exceptions for the repo-on-file tool."""


import click


class RepoOnFireException(click.ClickException):
    """Base class for all exceptions raised by repo-on-fire itself."""
