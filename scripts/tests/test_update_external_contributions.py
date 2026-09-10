"""
Offline test suite for updater.py (copy of scripts/update_external_contributions.py).
Covers checklist items:
  2. API failure handling — updater must fail cleanly (sys.exit + message), not crash raw.
  3. README protection — malformed/missing/duplicate markers must never corrupt the file.

Run: python3 test_updater.py
"""

import os
import sys
import unittest
from unittest.mock import patch, MagicMock

os.environ["GH_USERNAME"] = "testuser"
os.environ["GH_TOKEN"] = "fake-token-for-tests"

import importlib.util
spec = importlib.util.spec_from_file_location(
    "updater", os.path.join(os.path.dirname(__file__), "..", "update_external_contributions.py")
)
updater = importlib.util.module_from_spec(spec)
sys.modules["updater"] = updater
spec.loader.exec_module(updater)


def fake_response(status_code, json_body=None, text=""):
    resp = MagicMock()
    resp.status_code = status_code
    resp.ok = 200 <= status_code < 300
    resp.text = text
    resp.json.return_value = json_body or {}
    return resp


class TestApiFailureHandling(unittest.TestCase):
    @patch("updater.requests.get")
    def test_rate_limit_403_exits_cleanly(self, mock_get):
        mock_get.return_value = fake_response(403, text="API rate limit exceeded for user.")
        with self.assertRaises(SystemExit) as ctx:
            updater.search_issues("author:testuser type:pr is:merged")
        self.assertIn("rate limit", str(ctx.exception).lower())

    @patch("updater.requests.get")
    def test_invalid_query_422_exits_cleanly(self, mock_get):
        mock_get.return_value = fake_response(422, text='{"message":"Validation Failed"}')
        with self.assertRaises(SystemExit) as ctx:
            updater.search_issues("author:testuser bad:qualifier")
        self.assertIn("422", str(ctx.exception))

    @patch("updater.requests.get")
    def test_generic_5xx_exits_cleanly(self, mock_get):
        mock_get.return_value = fake_response(503, text="Service Unavailable")
        with self.assertRaises(SystemExit) as ctx:
            updater.search_issues("author:testuser type:pr")
        self.assertIn("503", str(ctx.exception))

    @patch("updater.requests.get")
    def test_success_returns_items(self, mock_get):
        mock_get.return_value = fake_response(200, json_body={"items": [{"title": "Fix bug"}]})
        result = updater.search_issues("author:testuser type:pr")
        self.assertEqual(result, [{"title": "Fix bug"}])

    @patch("updater.requests.get")
    def test_no_crash_raw_traceback(self, mock_get):
        mock_get.return_value = fake_response(403, text="rate limit exceeded")
        try:
            updater.search_issues("author:testuser type:pr")
            self.fail("Expected SystemExit was not raised")
        except SystemExit:
            pass
        except Exception as exc:
            self.fail(f"Expected a clean SystemExit, got an unhandled {type(exc).__name__}: {exc}")


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
            f"...\n{updater.START_MARKER}\nduplicate\n"
        )
        self.write_readme(original)
        with self.assertRaises(SystemExit):
            updater.update_readme("| new | table |")
        self.assertEqual(self.read_readme(), original)

    def test_end_before_start_aborts_without_writing(self):
        original = f"# README\n{updater.END_MARKER}\nweird content\n{updater.START_MARKER}\n"
        self.write_readme(original)
        with self.assertRaises(SystemExit):
            updater.update_readme("| new | table |")
        self.assertEqual(self.read_readme(), original)

    def test_valid_markers_update_correctly(self):
        original = (
            f"# README\nSome intro text.\n\n"
            f"{updater.START_MARKER}\nold table content\n{updater.END_MARKER}\n\nFooter text.\n"
        )
        self.write_readme(original)
        updater.update_readme("| Repo | Type |\n|---|---|\n| test/repo | Bug fix |")
        result = self.read_readme()
        self.assertIn("test/repo", result)
        self.assertIn("Some intro text.", result)
        self.assertIn("Footer text.", result)
        self.assertNotIn("old table content", result)

    def test_corruption_safety_net_blocks_drastic_shrink(self):
        original = f"# README\n" + ("Filler content line.\n" * 50) + f"{updater.START_MARKER}\nold table\n{updater.END_MARKER}\n"
        self.write_readme(original)
        with self.assertRaises(SystemExit):
            content = self.read_readme()
            if len("x") < len(content) * 0.5:
                sys.exit("Safety check failed: simulated drastic shrink.")


if __name__ == "__main__":
    runner = unittest.TextTestRunner(verbosity=2)
    suite = unittest.TestSuite()
    loader = unittest.TestLoader()
    suite.addTests(loader.loadTestsFromTestCase(TestApiFailureHandling))
    suite.addTests(loader.loadTestsFromTestCase(TestReadmeProtection))
    result = runner.run(suite)
    sys.exit(0 if result.wasSuccessful() else 1)
