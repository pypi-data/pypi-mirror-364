import re
import argparse
from pathlib import Path
from typing import List


def add_changelog_path_argument(parser: argparse.ArgumentParser) -> argparse.ArgumentParser:
    """
    Add a positional argument for the changelog path.
    """

    return parser.add_argument(
        "changelog_path",
        nargs="?",
        default=Path.cwd(),
        help="Path to the changelog file to process. Default path is the current directory. "
        "If the filename is not provided, it'll look for a CHANGELOG.md file.",
    )


def add_include_unreleased_argument(parser: argparse.ArgumentParser) -> argparse.ArgumentParser:
    """
    Add an argument to be able to include Unreleased section when perform actions on a changelog file.
    """

    return parser.add_argument(
        "--include_unreleased",
        default=False,
        action="store_true",
        help="Include unreleased items to the output. By default, only released items are included.",
    )


def sanitize_changelog_path(changelog_path: Path) -> Path:
    """
    Check that the given path points to a valid file and if a file named CHANGELOG.md exists in the given directory.

    Return a valid changelog path.
    """

    if not changelog_path.is_file():
        changelog_path = changelog_path / "CHANGELOG.md"

    if not changelog_path.is_file():
        raise FileNotFoundError(f"The changelog file {changelog_path} doesn't exist.")

    return changelog_path


def read_changelog_path(changelog_path: Path) -> List[str]:
    """
    Open and read a changelog path.

    Return a splited changelog file.
    """

    changelog_file = changelog_path.read_text()

    return changelog_file.split("\n")


def get_version_line_pattern(changelog_format: str = "markdown") -> str:
    """
    Returns version line pattern depending on changelog file format.
    """

    if changelog_format == "markdown":
        return r"^## \[(.+)\]"


def get_version_pattern(version: str) -> str:
    """
    Use a provided version to create a pattern.
    """

    return rf"^## \[{re.escape(version)}\]"


def get_version(changelog_file: list, include_unreleased: bool, get_initial: bool = False) -> str:
    """
    Find and return initial version of a changelog file.
    """

    if get_initial:
        changelog_file = reversed(changelog_file)

    for line in changelog_file:
        current_version = re.search(get_version_line_pattern(), line)

        # If current_version isn't found or we found Unreleased section we continue, unless include_unreleased is set to True
        if current_version is None or (current_version.group(1) == "Unreleased" and not include_unreleased):
            continue
        return current_version.group(1)
    # If no version has been found, we throw an error.
    raise RuntimeError("Couldn't find a version line in the file: ")


def get_latest_version(changelog_file: list, include_unreleased: bool) -> str:
    """
    Return latest version of a changelog file.
    """

    return get_version(changelog_file, include_unreleased)


def get_initial_version(changelog_file: list, include_unreleased: bool) -> str:
    """
    Return initial version of a changelog file.
    """

    return get_version(changelog_file, include_unreleased, True)


def is_version_in_changelog(changelog_file: list, version: str) -> bool:
    """
    Check if given version exists in the given changelog file.
    """

    for line in changelog_file:
        if re.search(rf"^## \[{version}]", line) is None:
            continue
        return True

    return False


def is_version_line(line: str) -> bool:
    """
    Check if the line is a line that contains a version.
    """

    if line.startswith("## ["):
        return True

    return False


def is_section_line(line: str) -> bool:
    """
    Check if the line is a section heading.
    """

    if line.startswith("###"):
        return True

    return False
