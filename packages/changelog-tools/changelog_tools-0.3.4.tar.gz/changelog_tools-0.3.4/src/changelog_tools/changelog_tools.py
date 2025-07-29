import argparse
from pathlib import Path
from .changelog_helpers.helpers import (
    add_changelog_path_argument,
    add_include_unreleased_argument,
    sanitize_changelog_path,
    read_changelog_path,
    get_latest_version,
)
from .changelog_helpers.summarize import get_summary


def add_get_parser(sub_commands_parser: argparse.ArgumentParser):
    """
    Define command line arguments for get feature.
    """

    get_parser = sub_commands_parser.add_parser("get", help="Check and display the latest version of a changelog file.")
    # Add argument to include Unreleased section of changelog or not
    add_include_unreleased_argument(get_parser)
    # Add argument to be able to choose another path for changelog file
    add_changelog_path_argument(get_parser)

    return get_parser


def get(arguments: argparse.Namespace):
    """
    Return latest version of a changelog file.
    """

    path = sanitize_changelog_path(Path(arguments.changelog_path))

    changelog_file = read_changelog_path(path)

    print(get_latest_version(changelog_file, arguments.include_unreleased))


def add_summarize_parser(sub_commands_parser: argparse.ArgumentParser):
    """
    Define command line arguments for summarize feature.
    """

    summarize_parser = sub_commands_parser.add_parser(
        "summarize",
        help="Check and display the changes list between two versions of a changelog file.",
    )

    summarize_parser.add_argument(
        "--old",
        help="Version from which we want the changes list. Default old version is the initial version of the changelog file.",
    )
    summarize_parser.add_argument(
        "--new",
        help="Version to which we want the changes list. Default new version is the latest version of the changelog file.",
    )
    # Add argument to include Unreleased section of changelog or not
    add_include_unreleased_argument(summarize_parser)
    # Add argument to be able to choose another path for changelog file
    add_changelog_path_argument(summarize_parser)

    return summarize_parser


def summarize(arguments: argparse.Namespace):
    """
    Return the changes list between two versions of a changelog file.
    """

    path = sanitize_changelog_path(Path(arguments.changelog_path))

    changelog_file = read_changelog_path(path)

    summaries, unassigned_items, old, new = get_summary(
        path, changelog_file, arguments.old, arguments.new, arguments.include_unreleased
    )

    print(f"# Changelog summary\n\nHere are all the changes between {old} and {new}:")
    # Display dict with changes sections sorted by alphabetic order
    for summary in sorted(summaries.keys()):
        print(f"\n{summary}\n")
        for change in summaries[summary]:
            print(change)
    if unassigned_items:
        print("\n/! WARNING: Following changes don't belong to any section:\n")
        for item in unassigned_items:
            print(item)


def main():
    import sys
    import argparse

    # Set up top level parser
    parser = argparse.ArgumentParser()

    # Set up sub_commands parser
    sub_commands = parser.add_subparsers(dest="command", title="Available commands")
    # Add all commands and their parameters
    add_get_parser(sub_commands)
    add_summarize_parser(sub_commands)

    arguments = parser.parse_args()

    try:
        if "get" == arguments.command:
            get(arguments)

        elif "summarize" == arguments.command:
            summarize(arguments)

        else:
            parser.print_help(sys.stderr)
            sys.exit(1)

    except Exception as e:
        print("An error occurred:", e, file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
