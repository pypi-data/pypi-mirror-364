"""Helper scripts used by the Workspace class."""

from argparse import ArgumentParser
from pathlib import Path
from subprocess import DEVNULL, CalledProcessError, check_call
from typing import List, Optional


class WorkspaceHelper:
    def run(self, args: Optional[List[str]] = None):
        parser = self._setup_parser()
        values = parser.parse_args(args)
        values.func(values)

    def _setup_parser(self) -> ArgumentParser:
        parser = ArgumentParser("Workspace Helper Scripts")
        sub_commands = parser.add_subparsers(title="Commands")

        checkout_command = sub_commands.add_parser(
            "checkout", help="Checkout a branch and notify if checkout was successful."
        )
        checkout_command.add_argument("branch")
        checkout_command.add_argument("stamp_file")
        checkout_command.set_defaults(func=self._checkout_and_notify)

        return parser

    def _checkout_and_notify(self, values):
        args = ["git", "checkout", values.branch]
        try:
            check_call(args, stderr=DEVNULL, stdout=DEVNULL)
            Path(values.stamp_file).touch()
        except CalledProcessError:
            # Accept git issues - this can be the case when the target branch
            # does not exist.
            pass


if __name__ == "__main__":
    WorkspaceHelper().run()
