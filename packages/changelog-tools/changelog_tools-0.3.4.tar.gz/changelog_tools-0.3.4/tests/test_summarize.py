# summarize.py

import os
import sys
import unittest
from pathlib import Path


sys.path.append(os.path.join(os.path.dirname(__file__), "../src"))
from changelog_tools.changelog_helpers.summarize import get_summary  # noqa: E402
from changelog_tools.changelog_helpers.helpers import (  # noqa: E402
    read_changelog_path,
    is_section_line,
    is_version_line,
    get_version_pattern,
    get_version_line_pattern,
)


expected_dict = {
    "### Added": [
        "- v1.1 Brazilian Portuguese translation.",
        "- v1.1 German Translation",
        "- v1.1 Spanish translation.",
        "- v1.1 Italian translation.",
        "- v1.1 Polish translation.",
        "- v1.1 Ukrainian translation.",
        "- Version navigation.",
    ],
    "### Changed": [
        "- Use frontmatter title & description in each language version template",
        "- Replace broken OpenGraph image with an appropriately-sized Keep a Changelog image that will render properly (although in English for all languages)",
        "- Fix OpenGraph title & description for all languages so the title and description when links are shared are language-appropriate",
    ],
    "### Removed": ["- Trademark sign previously shown after the project description in version"],
    "### Fixed": [
        "- Improve French translation (#377).",
        "- Improve id-ID translation (#416).",
        "- Improve Persian translation (#457).",
    ],
}

expected_dict_with_unreleased = {
    "### Added": [
        '- Answer "Should you ever rewrite a change log?".',
        "- v1.1 Brazilian Portuguese translation.",
        "- v1.1 German Translation",
        "- v1.1 Spanish translation.",
        "- v1.1 Italian translation.",
        "- v1.1 Polish translation.",
        "- v1.1 Ukrainian translation.",
        "- Version navigation.",
    ],
    "### Changed": [
        "- Use frontmatter title & description in each language version template",
        "- Replace broken OpenGraph image with an appropriately-sized Keep a Changelog image that will render properly (although in English for all languages)",
        "- Fix OpenGraph title & description for all languages so the title and description when links are shared are language-appropriate",
    ],
    "### Removed": ["- Trademark sign previously shown after the project description in version"],
    "### Fixed": [
        "- Improve French translation (#377).",
        "- Improve id-ID translation (#416).",
        "- Improve Persian translation (#457).",
    ],
}


class SummarizeTest(unittest.TestCase):
    def setUp(self):
        self.semver_changelog_path = Path("data/CHANGELOG_SEM_VER.md")
        self.semver_changelog_file = read_changelog_path(self.semver_changelog_path)
        self.expected_unassigned_items = ['- New "Guiding Principles" sub-section to "How do I make a changelog?".']

    def test_summarize(self):
        """
        Test that we get all changes between two versions of a changelog file, grouped by changes type.
        """

        # Test that an error is raised if we provide a version that does not exist in the changelog file
        with self.assertRaises(Exception):
            get_summary(self.semver_changelog_path, "0.0.0", "1.0.1")
        # Test that an error is raised if we provide versions in invalid order
        with self.assertRaises(Exception):
            get_summary(
                self.semver_changelog_path,
                self.semver_changelog_file,
                "1.0.3",
                "1.0.1",
                False,
            )
        # Test that default version is set correctly if we provide only one version
        self.assertTrue(
            get_summary(
                self.semver_changelog_path,
                self.semver_changelog_file,
                None,
                "1.0.1",
                False,
            )
        )
        # Test that default versions are set correctly if no version is provided
        self.assertTrue(
            get_summary(
                self.semver_changelog_path,
                self.semver_changelog_file,
                None,
                None,
                False,
            )
        )
        # Test that default versions are set correctly if one version is provided and if we include Unreleased
        self.assertTrue(
            get_summary(
                self.semver_changelog_path,
                self.semver_changelog_file,
                None,
                "Unreleased",
                True,
            )
        )
        # Test that default versions are set correctly if no version is provided and if we include Unreleased
        self.assertTrue(get_summary(self.semver_changelog_path, self.semver_changelog_file, None, None, True))

        # Test that we return correct version line pattern for markdown changelog file
        self.assertTrue(get_version_line_pattern(), "^## [(.+)]")
        self.assertFalse(get_version_line_pattern("debian"), "^## [(.+)]")

        # Test that only string starting with ## [ are version line
        self.assertTrue(is_version_line("## [1.0.1]"))
        self.assertFalse(is_version_line("Version line without markdown heading."))
        # Test that only string starting with ### are section line
        self.assertTrue(is_section_line("### Added"))
        self.assertFalse(is_section_line("Section line without markdown heading."))

        # Test that get_version_pattern return expected pattern for the given version
        self.assertEqual(get_version_pattern("0.0.1"), "^## \\[0\\.0\\.1\\]")

        print("Test summary...")
        found_changes, unassigned_items, start, end = get_summary(
            self.semver_changelog_path,
            self.semver_changelog_file,
            "1.0.1",
            "1.0.3",
            False,
        )
        # Test that expected content without unreleased matches with found content
        self.assertEqual(expected_dict, found_changes)
        found_changes_with_unreleased, unassigned_items_with_unreleased, start, end = get_summary(
            self.semver_changelog_path,
            self.semver_changelog_file,
            "1.0.1",
            "Unreleased",
            True,
        )
        # Test that expected content with unreleased matches with found content
        self.assertEqual(expected_dict_with_unreleased, found_changes_with_unreleased)
        # Test that unassigned_items are stored correctly in a list
        self.assertEqual(self.expected_unassigned_items, unassigned_items_with_unreleased)


if __name__ == "__main__":
    unittest.main()
