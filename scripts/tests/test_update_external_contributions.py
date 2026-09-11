"""
Offline test suite for update_external_contributions.py.

Covers:
  - API failure handling
  - README marker count/order protection
  - dashboard anchor protection
  - drastic-shrink safety protection
"""

import os
import sys
import unittest
from unittest.mock import MagicMock, patch

os.environ["GH_USERNAME"] = "testuser"
os.environ["GH_TOKEN"] = "fake-token-for-tests"

import importlib.util

spec = importlib.util.spec_from_file_location(
    "updater", os.path.join(os.path.dirname(__file__), "..", "update_external_contributions.py")
)
updater = importlib.util.module_from_spec(spec)
sys.modules["updater"] = updater
spec.loader.exec_module(updater)


class TestApiFailureHandling(unittest.TestCase):
    @patch("updater.github_get")
    def test_rate_limit_403_exits_cleanly(self, mock_get):
        mock_get.side_effect = SystemExit("GitHub Search API rate limit hit")
        with self.assertRaises(SystemExit) as ctx:
            updater.search_issues("author:testuser type:pr is:merged")
        self.assertIn("rate limit", str(ctx.exception).lower())

    @patch("updater.github_get")
    def test_invalid_query_422_exits_cleanly(self, mock_get):
        mock_get.side_effect = SystemExit("GitHub rejected the search query as invalid (422)")
        with self.assertRaises(SystemExit) as ctx:
            updater.search_issues("author:testuser bad:qualifier")
        self.assertIn("422", str(ctx.exception))

    @patch("updater.github_get")
    def test_generic_5xx_exits_cleanly(self, mock_get):
        mock_get.side_effect = SystemExit("GitHub Search API request failed (503)")
        with self.assertRaises(SystemExit) as ctx:
            updater.search_issues("author:testuser type:pr")
        self.assertIn("503", str(ctx.exception))

    @patch("updater.github_get")
    def test_success_returns_items(self, mock_get):
        mock_get.return_value = {"items": [{"title": "Fix bug"}]}
        result = updater.search_issues("author:testuser type:pr")
        self.assertEqual(result, [{"title": "Fix bug"}])


class TestReadmeProtection(unittest.TestCase):
    def setUp(self):
        self.readme_path = "README.md"
        updater.README_PATH = self.readme_path

    def tearDown(self):
        if os.path.exists(self.readme_path):
            os.remove(self.readme_path)

    def write_readme(self, content):
        with open(self.readme_path, "w", encoding="utf-8") as f:
            f.write(content)

    def read_readme(self):
        with open(self.readme_path, "r", encoding="utf-8") as f:
            return f.read()

    def test_missing_markers_aborts_without_writing(self):
        original = "# My README\nNo markers here at all.\n"
        self.write_readme(original)
        with self.assertRaises(SystemExit):
            updater.update_readme("| a | b |")
        self.assertEqual(self.read_readme(), original)

    def test_duplicate_start_marker_aborts_without_writing(self):
        original = (
            f"# README\n{updater.START_MARKER}\nold table\n{updater.END_MARKER}\n"
            f"...\n{updater.START_MARKER}\nduplicate\n{updater.END_MARKER}\n"
        )
        self.write_readme(original)
        with self.assertRaises(SystemExit):
            updater.update_readme("| new | table |")
        self.assertEqual(self.read_readme(), original)

    def test_end_before_start_aborts_without_writing(self):
        original = (
            f"# README\n{updater.END_MARKER}\nweird content\n"
            f"{updater.START_MARKER}\n"
        )
        self.write_readme(original)
        with self.assertRaises(SystemExit):
            updater.update_readme("| new | table |")
        self.assertEqual(self.read_readme(), original)

    def test_valid_markers_update_correctly(self):
        original = (
            f"# README\nSome intro text.\n\n"
            f"{updater.START_MARKER}\nold table content\n{updater.END_MARKER}\n\n"
            f"{updater.DASHBOARD_ANCHOR}\n\n{updater.DASHBOARD_HEADING}\n\nFooter text.\n"
        )
        self.write_readme(original)
        updater.update_readme("| Repo | Type |\n|---|---|\n| test/repo | Bug fix |")
        result = self.read_readme()
        self.assertIn("test/repo", result)
        self.assertIn("Some intro text.", result)
        self.assertIn("Footer text.", result)
        self.assertNotIn("old table content", result)
        self.assertEqual(result.count(updater.DASHBOARD_ANCHOR), 1)

    def test_duplicate_dashboard_heading_aborts_without_writing(self):
        original = (
            f"# README\n{updater.START_MARKER}\nold\n{updater.END_MARKER}\n"
            f"{updater.DASHBOARD_HEADING}\n{updater.DASHBOARD_HEADING}\n"
        )
        self.write_readme(original)
        with self.assertRaises(SystemExit):
            updater.update_readme("| new | table |")
        self.assertEqual(self.read_readme(), original)

    def test_corruption_safety_net_blocks_drastic_shrink(self):
        original = (
            "# README\n" + ("Filler content line.\n" * 50) +
            f"{updater.START_MARKER}\nold table\n{updater.END_MARKER}\n"
            f"{updater.DASHBOARD_HEADING}\n"
        )
        self.write_readme(original)
        with patch.object(updater, "ensure_dashboard_anchor", return_value="x"):
            with self.assertRaises(SystemExit) as ctx:
                updater.update_readme("x")
        self.assertIn("less than half", str(ctx.exception))
        self.assertEqual(self.read_readme(), original)


if __name__ == "__main__":
    unittest.main(verbosity=2)
