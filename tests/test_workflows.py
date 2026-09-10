import unittest
from pathlib import Path

import yaml


ROOT = Path(__file__).parents[1]
WORKFLOWS = ROOT / ".github" / "workflows"


class WorkflowTests(unittest.TestCase):
    def test_workflows_parse_and_use_pinned_major_actions(self):
        for path in WORKFLOWS.glob("*.yml"):
            with self.subTest(workflow=path.name):
                data = yaml.safe_load(path.read_text(encoding="utf-8"))
                self.assertIsInstance(data, dict)
                jobs = data.get("jobs")
                self.assertIsInstance(jobs, dict)
                text = path.read_text(encoding="utf-8")
                self.assertNotIn("@master", text)
                self.assertNotIn("@v4", text)

    def test_snake_workflow_targets_main_assets(self):
        path = WORKFLOWS / "snake.yml"
        text = path.read_text(encoding="utf-8")
        self.assertIn("actions/checkout@v5", text)
        self.assertIn("Platane/snk@v3", text)
        self.assertIn("git push origin HEAD:main", text)
        self.assertIn("assets/github-contribution-grid-snake.svg", text)

    def test_external_contributions_workflow_runs_script(self):
        path = WORKFLOWS / "external-contributions.yml"
        text = path.read_text(encoding="utf-8")
        self.assertIn("actions/checkout@v5", text)
        self.assertIn("actions/setup-python@v6", text)
        self.assertIn("python scripts/update_external_contributions.py", text)
        self.assertIn("contents: write", text)


if __name__ == "__main__":
    unittest.main()
