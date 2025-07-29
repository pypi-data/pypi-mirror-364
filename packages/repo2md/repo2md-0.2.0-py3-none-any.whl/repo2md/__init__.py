import enum
import logging
import sys

import click

from repo2md.main import convert_repo_to_md, generate_markdown  # noqa: F401
from repo2md.utils import (  # noqa: F401
    IGNORE_DIRECTORIES,
    IGNORE_FILES,
    LANGUAGE_EXTENSIONS,
)

version = "0.2.0"

LOGGER = logging.getLogger("repo2md")
handler = logging.StreamHandler()
handler.setFormatter(
    fmt=logging.Formatter(
        fmt="%(asctime)s - %(levelname)s - [%(name)s:%(funcName)s:%(lineno)d] - %(message)s",
        datefmt="%b-%d-%Y %H:%M:%S",
    )
)
LOGGER.setLevel(level=logging.INFO)
LOGGER.addHandler(hdlr=handler)


class Command(enum.Enum):
    """Enum to represent the available commands for the commandline interface."""

    GITHUB = "github"
    LOCAL = "local"


def print_help(command: Command = None, bold: bool = False) -> None:
    """Prints the help section for the commandline interface."""
    options = {
        "--version | -V": "Prints the version.",
        "--help | -H": "Prints the help section.",
    }
    arbitrary = f"\nCommand: {command.value}" if command else ""
    if command == Command.GITHUB:
        options = {
            "--repo | -R": "Name of the GitHub repository to convert.",
            "--owner | -O": "Name of the GitHub repository's owner/organization.",
            "--branch | -B": "Branch of the repository to use (default is None, which uses the default branch).",
            "--clean | -C": "Boolean flag to delete the repository after conversion (default is 'True').",
            "--language | -L": "Boolean flag to filter files by language (default is False).",
            "--destination | -D": "Destination directory to store the Markdown file (default is 'tmp').",
        }
    elif command == Command.LOCAL:
        options = {
            "--source | -S": "Source path to the local repo.",
            "--destination | -D": "Destination directory to store the Markdown file (default is 'tmp').",
            "--language | -L": "Programming language of the code files in source path (default is None).",
        }
    else:
        arbitrary = (
            "\nUsage: repo2md [arbitrary-command]"
            "\n\nCommands:"
            "\n\t* github: Initiates the conversion process."
            "\n\t* local: Uses a local directory as the source for conversion."
        )
    # unique way to increase spacing to keep all values monotonic
    _longest_key = len(max(options.keys()))
    _pretext = "\n\t* "
    choices = _pretext + _pretext.join(
        f"{k} {'·' * (_longest_key - len(k) + 8)}→ {v}".expandtabs()
        for k, v in options.items()
    )
    click.secho(f"{arbitrary}" f"\n\nOptions:{choices}\n", bold=bold, err=True)


def rename_io_map(command: Command, **kwargs) -> dict:
    """Renames the keyword arguments to match the expected parameters for the conversion functions.

    Args:
        command: The command being executed (GITHUB or LOCAL).
        **kwargs: Keyword arguments to be renamed.

    Returns:
        dict:
        A dictionary with the renamed keyword arguments.
    """
    if command == Command.GITHUB:
        kwargs_map = {
            "repo": "repo_name",
            "language": "language_filter",
            "clean": "delete",
        }
    elif command == Command.LOCAL:
        kwargs_map = {
            "source": "source_repo_path",
            "language": "source_repo_language",
        }
    else:
        # This should never happen, but just in case
        raise RuntimeError(f"Unknown command: {command}")
    final_kwargs = {}
    for key, value in kwargs.items():
        if kwargs_map.get(key):
            final_kwargs[kwargs_map[key]] = value
        else:
            final_kwargs[key] = value
    return final_kwargs


@click.command()
@click.argument("github", required=False)
@click.argument("local", required=False)
@click.option("--version", "-V", is_flag=True, help="Prints the version.")
@click.option("--help", "-H", is_flag=True, help="Prints the help section.")
@click.option("--repo", "-R", help="Name of the GitHub repository to convert.")
@click.option("--owner", "-O", help="Name of the GitHub repository to convert.")
@click.option(
    "--branch",
    "-B",
    help="Branch of the repository to use (default is None, which uses the default branch).",
)
@click.option(
    "--destination",
    "-D",
    help="Output directory to store the Markdown file (default is 'tmp').",
    default="tmp",
)
@click.option(
    "--clean",
    "-C",
    help="Boolean flag to delete the repository after conversion (default is True).",
    is_flag=False,
    default=True,
)
@click.option(
    "--language",
    "-L",
    help="Boolean flag to filter files by language (default is False).",
    is_flag=True,
    default=False,
)
@click.option(
    "--source",
    "-S",
    help="Source path to a repo if a directory has been downloaded already.",
)
def commandline(*_, **kwargs) -> None:
    # noinspection GrazieInspection
    """Starter function to construct a markdown file from a GitHub repository.

    Notes:
        Flags can have different meanings based on the command used.
    """
    assert sys.argv[0].lower().endswith("repo2md"), "Invalid commandline trigger!!"

    if kwargs.get("version"):
        click.secho(f"repo2md {version}", bold=True)
        sys.exit(0)
    try:
        command = Command[kwargs.get(Command.GITHUB.value, Command.LOCAL.value).upper()]
    except AttributeError:
        print_help(bold=True)
        sys.exit(1)

    if kwargs.get("help"):
        print_help(command, bold=True)
        sys.exit(0)

    if command == Command.GITHUB:
        assert kwargs.get("repo"), "\n\t--repo flag is mandatory for GitHub repository!"
        convert_repo_to_md(**rename_io_map(command, **kwargs))
    elif command == Command.LOCAL:
        assert kwargs.get(
            "source"
        ), "\n\t--source flag is mandatory for local repository!"
        convert_repo_to_md(**rename_io_map(command, **kwargs))
    else:
        print_help()
        sys.exit(1)
