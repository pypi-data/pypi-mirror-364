import re
from pathlib import Path
from .helpers import (
    is_version_in_changelog,
    get_latest_version,
    get_initial_version,
    get_version_pattern,
    is_version_line,
    is_section_line,
)
from typing import Dict, List


def generate_summary(changelog_file: list, top: str, bottom: str) -> Dict[str, List[str]]:
    """
    Summarise all the types of changes that have been made between two provided versions.

    Parameters
    - changelog_path: Path of the changelog we want to extract parts.
    - top: Version from which we want to start extract changes. This is the first version we'll need to find with for loop.
    - bottom: Version to which we want to stop extract changes. This is the last version we'll need to find with for loop.

    Return a dict with a short header that reminds top/bottom versions and all different kind of found sections, grouped by type of change.
    """

    current_section = None
    extract_on = False
    complete_on = False
    result = {}
    unassigned_items = []

    for line in changelog_file:
        # Everytime an empty line is found, it's ignored
        if line == "":
            continue
        # When we find the first version, we set a bool to True, which means we can begin to appends line in our dict
        if re.match(get_version_pattern(top), line):
            extract_on = True
        # When we met a new version, we set current_section to None, in case we met changes without sections
        if extract_on and is_version_line(line):
            current_section = None
        # When we find a heading section line, we can set current_version with current line
        if extract_on and is_section_line(line):
            current_section = line
        # Define current_section allow us to tell that all following lines can be added to the dict with current_section as a key
        if extract_on and not is_section_line(line) and not is_version_line(line):
            if current_section in result:
                result[current_section].append(line)
            # In case section header is missing, we still want to keep unassigned items
            elif current_section is None:
                unassigned_items.append(line)
            else:
                result[current_section] = [line]
        # When we find the other version, we set a bool to True, in order to continue adding following lines
        # until another version is found or the end of file is reached
        if re.match(get_version_pattern(bottom), line):
            complete_on = True
            continue
        if complete_on and is_version_line(line):
            break

    return result, unassigned_items


def get_summary(changelog_path: Path, changelog_file: list, old: str, new: str, include_unreleased: bool):
    """
    Set values for old and new versions and check if old/new versions exist in changelog file, otherwise raise an error.
    """

    # If old version is not provided, we set initial version as default value.
    if old is None:
        old = get_initial_version(changelog_file, include_unreleased)
    # If new version is not provided, we set latest version as default value.
    if new is None:
        new = get_latest_version(changelog_file, include_unreleased)
    # If versions are provided in invalid order, we raise an error
    if old > new:
        raise RuntimeError(
            f"Versions are provided in invalid order. Old version '{old}' shouldn't be higher than the new version '{new}'."
        )
    # If old version does not exist in the changelog file, we raise an error
    if not is_version_in_changelog(changelog_file, old):
        raise RuntimeError(f"Old version '{old}' does not exist in {changelog_path}.")
    # If new version does not exist in the changelog file, we raise an error
    if not is_version_in_changelog(changelog_file, new):
        raise RuntimeError(f"New version '{new}' does not exist in {changelog_path}.")

    # Now, that we are sure that we get correct versions, we can read the changelog file to get what we need
    summary, unassigned_items = generate_summary(changelog_file, new, old)

    return summary, unassigned_items, old, new
