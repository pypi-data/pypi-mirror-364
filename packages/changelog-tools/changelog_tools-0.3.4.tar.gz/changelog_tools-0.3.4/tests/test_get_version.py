# get.py

import os
import sys
import unittest
from pathlib import Path


sys.path.append(os.path.join(os.path.dirname(__file__), "../src"))
from changelog_tools.changelog_helpers.helpers import (  # noqa 420
    get_latest_version,
    get_initial_version,
    is_version_in_changelog,
    read_changelog_path,
)


class GetVersionTest(unittest.TestCase):
    def setUp(self):
        self.semver_changelog_path = read_changelog_path(Path("data/CHANGELOG_SEM_VER.md"))
        self.no_semver_changelog_path = read_changelog_path(Path("data/CHANGELOG_NO_SEM_VER.md"))
        self.latest_semver_version = get_latest_version(self.semver_changelog_path, False)
        self.latest_no_semver_version = get_latest_version(self.no_semver_changelog_path, False)
        self.initial_semver_version = get_initial_version(self.semver_changelog_path, False)
        self.initial_no_semver_version = get_initial_version(self.no_semver_changelog_path, False)

    def test_changelog_file(self):
        """
        Test to get version with a file that isn't a changelog file.
        Test to get version without providing a file.
        """

        path = Path("README.md")

        with self.assertRaises(Exception):
            get_latest_version(path)

        with self.assertRaises(Exception):
            get_latest_version()

    def test_get_latest_version(self):
        """
        Test that we get the latest version number, even if it don't respect semantic versioning.
        """

        print("Test version number...")
        self.assertEqual(self.latest_semver_version, "1.0.3")
        self.assertEqual(self.latest_no_semver_version, "14.0.6-5A.5.0.0.202304182122")

    def test_get_initial_version(self):
        """
        Test that we get the initial version number, even if it don't respect semantic versioning.
        """

        self.assertEqual(self.initial_semver_version, "1.0.0")
        self.assertEqual(self.initial_no_semver_version, "1:2.30.2-1+deb11u2")

    def test_is_version_in_changelog(self):
        """
        Test that we check correctly if a given version exists or not.
        """

        self.assertFalse(is_version_in_changelog(self.semver_changelog_path, "0.0.0"))
        self.assertTrue(is_version_in_changelog(self.semver_changelog_path, "1.0.0"))


if __name__ == "__main__":
    unittest.main()
