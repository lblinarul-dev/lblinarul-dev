import importlib.util
import os
import sys
import unittest
from unittest.mock import MagicMock, patch

os.environ["GH_USERNAME"] = "testuser"
os.environ["GH_TOKEN"] = "fake-token"

spec = importlib.util.spec_from_file_location(
    "own_updater",
    os.path.join(os.path.dirname(__file__), "..", "update_own_projects.py"),
)
own_updater = importlib.util.module_from_spec(spec)
sys.modules["own_updater"] = own_updater
spec.loader.exec_module(own_updater)


def fake_response(status_code, json_body=None, text=""):
    response = MagicMock()
    response.status_code = status_code
    response.ok = 200 <= status_code < 300
    response.text = text
    response.json.return_value = json_body if json_body is not None else {}
    return response


class TestFetchOwnRepos(unittest.TestCase):
    @patch("own_updater.requests.get")
    def test_excludes_forks_and_profile_repo(self, mock_get):
        mock_get.return_value = fake_response(
            200,
            json_body=[
                {
                    "name": "real-project",
                    "fork": False,
                    "visibility": "public",
                    "description": "A real thing",
                    "pushed_at": "2026-09-01T00:00:00Z",
                    "html_url": "https://github.com/testuser/real-project",
                },
                {
                    "name": "forked-repo",
                    "fork": True,
                    "visibility": "public",
                    "description": "not mine originally",
                    "pushed_at": "2026-09-01T00:00:00Z",
                    "html_url": "https://github.com/testuser/forked-repo",
                },
                {
                    "name": "testuser",
                    "fork": False,
                    "visibility": "public",
                    "description": "profile README repo",
                    "pushed_at": "2026-09-01T00:00:00Z",
                    "html_url": "https://github.com/testuser/testuser",
                },
            ],
        )
        repos = own_updater.fetch_own_repos()
        names = [repo["name"] for repo in repos]
        self.assertIn("real-project", names)
        self.assertNotIn("forked-repo", names)
        self.assertNotIn("testuser", names)

    @patch("own_updater.requests.get")
    def test_rate_limit_exits_cleanly(self, mock_get):
        mock_get.return_value = fake_response(403, text="API rate limit exceeded")
        with self.assertRaises(SystemExit):
            own_updater.fetch_own_repos()

    @patch("own_updater.requests.get")
    def test_404_exits_cleanly(self, mock_get):
        mock_get.return_value = fake_response(404, text="Not Found")
        with self.assertRaises(SystemExit):
            own_updater.fetch_own_repos()


class TestRendering(unittest.TestCase):
    def test_render_table_empty(self):
        table = own_updater.render_table([])
        self.assertIn("no public repositories found", table)

    def test_render_table_with_repo(self):
        table = own_updater.render_table(
            [
                {
                    "name": "cool-app",
                    "description": "does cool stuff",
                    "pushed_at": "2026-08-15T00:00:00Z",
                    "html_url": "https://github.com/testuser/cool-app",
                }
            ]
        )
        self.assertIn("cool-app", table)
        self.assertIn("does cool stuff", table)
        self.assertIn("2026-08-15", table)

    def test_escapes_pipe_and_newline(self):
        table = own_updater.render_table(
            [
                {
                    "name": "cool|app",
                    "description": "line one\nline two | detail",
                    "pushed_at": "2026-08-15T00:00:00Z",
                    "html_url": "https://github.com/testuser/cool-app",
                }
            ]
        )
        self.assertIn("cool\\|app", table)
        self.assertIn("line one line two \\| detail", table)


class TestReadmeProtection(unittest.TestCase):
    def setUp(self):
        own_updater.README_PATH = "README_own.md"

    def tearDown(self):
        if os.path.exists("README_own.md"):
            os.remove("README_own.md")

    def write_readme(self, content):
        with open("README_own.md", "w", encoding="utf-8") as file:
            file.write(content)

    def test_missing_markers_aborts(self):
        self.write_readme("# No markers here\n")
        with self.assertRaises(SystemExit):
            own_updater.update_readme("| a |")

    def test_duplicate_markers_abort(self):
        content = (
            f"{own_updater.START_MARKER}\nold\n{own_updater.END_MARKER}\n"
            f"{own_updater.START_MARKER}\nsecond\n{own_updater.END_MARKER}\n"
        )
        self.write_readme(content)
        with self.assertRaises(SystemExit):
            own_updater.update_readme("| new |")

    def test_end_before_start_aborts(self):
        self.write_readme(
            f"{own_updater.END_MARKER}\ntext\n{own_updater.START_MARKER}\n"
        )
        with self.assertRaises(SystemExit):
            own_updater.update_readme("| new |")

    def test_valid_update_preserves_surrounding_content(self):
        content = (
            f"# R\nintro\n{own_updater.START_MARKER}\nold\n"
            f"{own_updater.END_MARKER}\nfooter\n"
        )
        self.write_readme(content)
        own_updater.update_readme("| new table |")
        with open("README_own.md", encoding="utf-8") as file:
            result = file.read()
        self.assertIn("new table", result)
        self.assertIn("intro", result)
        self.assertIn("footer", result)
        self.assertNotIn("old", result)


if __name__ == "__main__":
    unittest.main(verbosity=2)
