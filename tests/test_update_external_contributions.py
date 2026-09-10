import importlib.util
import sys
import unittest
from pathlib import Path
from unittest.mock import patch


SCRIPT_PATH = Path(__file__).parents[1] / "scripts" / "update_external_contributions.py"


spec = importlib.util.spec_from_file_location("update_external_contributions", SCRIPT_PATH)
if spec is None or spec.loader is None:
    raise RuntimeError(f"Could not load {SCRIPT_PATH}")
module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = module
spec.loader.exec_module(module)


class UpdateExternalContributionsTests(unittest.TestCase):
    def test_render_table_escapes_pipe_and_newline(self):
        rows = [("2026-01-01", "owner/repo", "Issue", "bad | title\nnext line", "[#1](https://github.com/owner/repo/issues/1)")]
        table = module.render_table(rows)
        self.assertIn("bad \\| title next line", table)
        self.assertEqual(table.count("\n"), 2)

    def test_ensure_dashboard_anchor_keeps_one_stable_anchor(self):
        content = "before\n\n<a id=\"-github-activity\"></a>\n\n## 📊 GitHub Activity\n\nafter\n"
        result = module.ensure_dashboard_anchor(content)
        self.assertEqual(result.count(module.DASHBOARD_ANCHOR), 1)
        self.assertEqual(result.count(module.DASHBOARD_HEADING), 1)
        self.assertIn(f"{module.DASHBOARD_ANCHOR}\n\n{module.DASHBOARD_HEADING}", result)

    def test_ensure_dashboard_anchor_rejects_duplicate_headings(self):
        content = "## 📊 GitHub Activity\n\n## 📊 GitHub Activity\n"
        with self.assertRaises(SystemExit):
            module.ensure_dashboard_anchor(content)

    def test_search_owned_repositories_filters_profile_repo_and_requires_public(self):
        payload = {
            "items": [
                {"name": "lblinarul-dev", "owner": {"login": "lblinarul-dev"}},
                {"name": "react-debugger", "owner": {"login": "lblinarul-dev"}},
                {"name": "other", "owner": {"login": "other"}},
            ]
        }
        with patch.object(module, "github_get", return_value=payload) as mocked_get:
            result = module.search_owned_repositories()

        self.assertEqual([repo["name"] for repo in result], ["react-debugger"])
        query = mocked_get.call_args.args[1]["q"]
        self.assertIn("is:public", query)
        self.assertIn("fork:false", query)
        self.assertIn("archived:false", query)

    def test_repo_name_from_issue(self):
        item = {"repository_url": "https://api.github.com/repos/example/project"}
        self.assertEqual(module.repo_name_from_issue(item), "example/project")


if __name__ == "__main__":
    unittest.main()
