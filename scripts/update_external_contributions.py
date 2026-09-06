"""
Update the README table with real external GitHub contributions.

The GitHub Actions workflow supplies GH_USERNAME and GH_TOKEN automatically.
"""

import os
import sys
from typing import Any

import requests

README_PATH = "README.md"
START_MARKER = "<!-- EXTERNAL-CONTRIBUTIONS:START -->"
END_MARKER = "<!-- EXTERNAL-CONTRIBUTIONS:END -->"
MAX_ROWS = 15
API_URL = "https://api.github.com/search/issues"

USERNAME = os.environ.get("GH_USERNAME", "").strip()
TOKEN = os.environ.get("GH_TOKEN", "").strip()

if not USERNAME:
    sys.exit("GH_USERNAME environment variable is required")

HEADERS = {
    "Accept": "application/vnd.github+json",
    "X-GitHub-Api-Version": "2022-11-28",
}
if TOKEN:
    HEADERS["Authorization"] = f"Bearer {TOKEN}"


def search_issues(query: str) -> list[dict[str, Any]]:
    """Search GitHub issues/PRs with clear errors and a bounded timeout."""
    try:
        response = requests.get(
            API_URL,
            headers=HEADERS,
            params={"q": query, "per_page": MAX_ROWS, "sort": "updated", "order": "desc"},
            timeout=30,
        )
        response.raise_for_status()
        data = response.json()
    except requests.RequestException as exc:
        sys.exit(f"GitHub API request failed: {exc}")

    items = data.get("items", [])
    if not isinstance(items, list):
        sys.exit("GitHub API returned an unexpected response")
    return items


def build_rows() -> list[tuple[str, str, str, str]]:
    """Return merged external PRs and opened external issues, newest first."""
    rows: list[tuple[str, str, str, str]] = []

    merged_prs = search_issues(f"author:{USERNAME} type:pr is:merged -user:{USERNAME}")
    for item in merged_prs:
        repo_url = item.get("repository_url", "")
        repo_full_name = "/".join(repo_url.rstrip("/").split("/")[-2:])
        if not repo_full_name or repo_full_name == "/":
            continue
        rows.append(
            (
                repo_full_name,
                "Merged PR",
                item.get("title", "Untitled PR"),
                f"[#{item.get('number')}]({item.get('html_url', '')})",
            )
        )

    opened_issues = search_issues(f"author:{USERNAME} type:issue -user:{USERNAME}")
    for item in opened_issues:
        repo_url = item.get("repository_url", "")
        repo_full_name = "/".join(repo_url.rstrip("/").split("/")[-2:])
        if not repo_full_name or repo_full_name == "/":
            continue
        rows.append(
            (
                repo_full_name,
                "Issue",
                item.get("title", "Untitled issue"),
                f"[#{item.get('number')}]({item.get('html_url', '')})",
            )
        )

    return rows[:MAX_ROWS]


def render_table(rows: list[tuple[str, str, str, str]]) -> str:
    """Render a safe Markdown table."""
    if not rows:
        return (
            "| Repo | Type | Description | Link |\n"
            "|---|---|---|---|\n"
            "| _(no external contributions recorded yet)_ | | | |"
        )

    lines = ["| Repo | Type | Description | Link |", "|---|---|---|---|"]
    for repo, kind, description, link in rows:
        repo = repo.replace("|", "\\|")
        kind = kind.replace("|", "\\|")
        description = description.replace("|", "\\|").replace("\n", " ")
        lines.append(f"| {repo} | {kind} | {description} | {link} |")
    return "\n".join(lines)


def update_readme(table_markdown: str) -> None:
    """Replace only the marked contribution table in README.md."""
    try:
        with open(README_PATH, "r", encoding="utf-8") as file:
            content = file.read()
    except OSError as exc:
        sys.exit(f"Could not read {README_PATH}: {exc}")

    if content.count(START_MARKER) != 1 or content.count(END_MARKER) != 1:
        sys.exit("README.md must contain exactly one external-contributions marker pair")

    before, remainder = content.split(START_MARKER, 1)
    _, after = remainder.split(END_MARKER, 1)
    new_content = f"{before}{START_MARKER}\n{table_markdown}\n{END_MARKER}{after}"

    if new_content == content:
        print("README.md is already up to date.")
        return

    try:
        with open(README_PATH, "w", encoding="utf-8") as file:
            file.write(new_content)
    except OSError as exc:
        sys.exit(f"Could not write {README_PATH}: {exc}")


def main() -> None:
    rows = build_rows()
    update_readme(render_table(rows))
    print(f"Updated {README_PATH} with {len(rows)} external contribution(s).")


if __name__ == "__main__":
    main()
