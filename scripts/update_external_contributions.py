"""
Update the README activity table with real GitHub projects and contributions.

The GitHub Actions workflow supplies GH_USERNAME and GH_TOKEN automatically.
The script keeps the README table limited to public repositories owned by the
profile plus PRs/issues authored by the profile in repositories they do not own.
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
REPO_SEARCH_URL = "https://api.github.com/search/repositories"

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


def github_get(url: str, params: dict[str, Any]) -> dict[str, Any]:
    """GET a GitHub API endpoint with clear errors and a bounded timeout."""
    try:
        response = requests.get(
            url,
            headers=HEADERS,
            params=params,
            timeout=30,
        )
        response.raise_for_status()
        data = response.json()
    except requests.RequestException as exc:
        sys.exit(f"GitHub API request failed: {exc}")

    if not isinstance(data, dict):
        sys.exit("GitHub API returned an unexpected response")
    return data


def search_issues(query: str) -> list[dict[str, Any]]:
    """Search GitHub issues/PRs."""
    data = github_get(
        API_URL,
        {"q": query, "per_page": MAX_ROWS, "sort": "updated", "order": "desc"},
    )
    items = data.get("items", [])
    if not isinstance(items, list):
        sys.exit("GitHub issue search returned an unexpected response")
    return items


def search_owned_repositories() -> list[dict[str, Any]]:
    """Return recent public repositories owned by the profile."""
    data = github_get(
        REPO_SEARCH_URL,
        {
            "q": f"user:{USERNAME} fork:false archived:false",
            "per_page": MAX_ROWS,
            "sort": "updated",
            "order": "desc",
        },
    )
    items = data.get("items", [])
    if not isinstance(items, list):
        sys.exit("GitHub repository search returned an unexpected response")
    return [
        item
        for item in items
        if item.get("owner", {}).get("login", "").lower() == USERNAME.lower()
        and item.get("name") != USERNAME
    ]


def repo_name_from_issue(item: dict[str, Any]) -> str:
    """Extract owner/name from a GitHub issue search result."""
    repo_url = str(item.get("repository_url", ""))
    parts = repo_url.rstrip("/").split("/")
    if len(parts) < 2:
        return ""
    return "/".join(parts[-2:])


def build_rows() -> list[tuple[str, str, str, str, str]]:
    """Return recent owned projects and external contributions, newest first."""
    rows: list[tuple[str, str, str, str, str]] = []

    for repo in search_owned_repositories():
        repo_name = repo.get("full_name", "")
        if not repo_name:
            continue
        rows.append(
            (
                str(repo.get("updated_at", "")),
                repo_name,
                "Project",
                repo.get("description") or "GitHub project",
                f"[Repo]({repo.get('html_url', '')})",
            )
        )

    merged_prs = search_issues(f"author:{USERNAME} type:pr is:merged")
    for item in merged_prs:
        repo_name = repo_name_from_issue(item)
        if not repo_name or repo_name.lower().startswith(f"{USERNAME.lower()}/"):
            continue
        rows.append(
            (
                str(item.get("updated_at", "")),
                repo_name,
                "Merged PR",
                item.get("title", "Untitled PR"),
                f"[#{item.get('number')}]({item.get('html_url', '')})",
            )
        )

    opened_issues = search_issues(f"author:{USERNAME} type:issue")
    for item in opened_issues:
        repo_name = repo_name_from_issue(item)
        if not repo_name or repo_name.lower().startswith(f"{USERNAME.lower()}/"):
            continue
        rows.append(
            (
                str(item.get("updated_at", "")),
                repo_name,
                "Issue",
                item.get("title", "Untitled issue"),
                f"[#{item.get('number')}]({item.get('html_url', '')})",
            )
        )

    rows.sort(key=lambda row: row[0], reverse=True)
    return rows[:MAX_ROWS]


def render_table(rows: list[tuple[str, str, str, str, str]]) -> str:
    """Render a safe Markdown table."""
    if not rows:
        return (
            "| Repo | Type | Description | Link |\n"
            "|---|---|---|---|\n"
            "| _(no GitHub activity recorded yet)_ | | | |"
        )

    lines = ["| Repo | Type | Description | Link |", "|---|---|---|---|"]
    for _, repo, kind, description, link in rows:
        repo = repo.replace("|", "\\|")
        kind = kind.replace("|", "\\|")
        description = description.replace("|", "\\|").replace("\n", " ")
        lines.append(f"| {repo} | {kind} | {description} | {link} |")
    return "\n".join(lines)


def update_readme(table_markdown: str) -> None:
    """Replace only the marked activity table in README.md."""
    try:
        with open(README_PATH, "r", encoding="utf-8") as file:
            content = file.read()
    except OSError as exc:
        sys.exit(f"Could not read {README_PATH}: {exc}")

    if content.count(START_MARKER) != 1 or content.count(END_MARKER) != 1:
        sys.exit("README.md must contain exactly one activity marker pair")

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
    print(f"Updated {README_PATH} with {len(rows)} GitHub activity item(s).")


if __name__ == "__main__":
    main()
