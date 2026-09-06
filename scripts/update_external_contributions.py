"""
Fetches this user's merged PRs and opened issues on repositories they do NOT own,
and rewrites the table between the EXTERNAL-CONTRIBUTIONS markers in README.md.

Run by .github/workflows/external-contributions.yml on a schedule, or manually:
    GH_USERNAME=your-username GH_TOKEN=ghp_xxx python scripts/update_external_contributions.py
"""

import os
import sys

import requests

README_PATH = "README.md"
START_MARKER = "<!-- EXTERNAL-CONTRIBUTIONS:START -->"
END_MARKER = "<!-- EXTERNAL-CONTRIBUTIONS:END -->"
MAX_ROWS = 15

USERNAME = os.environ.get("GH_USERNAME")
TOKEN = os.environ.get("GH_TOKEN")

if not USERNAME:
    sys.exit("GH_USERNAME environment variable is required")

HEADERS = {
    "Accept": "application/vnd.github+json",
    "X-GitHub-Api-Version": "2022-11-28",
}

if TOKEN:
    HEADERS["Authorization"] = f"Bearer {TOKEN}"


def search_issues(query: str) -> list[dict]:
    """Calls the GitHub Search API and returns the items list."""
    url = "https://api.github.com/search/issues"
    resp = requests.get(
        url,
        headers=HEADERS,
        params={"q": query, "per_page": MAX_ROWS, "sort": "updated"},
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json().get("items", [])


def build_rows() -> list[tuple[str, str, str, str]]:
    """
    Returns rows of (repo, type, description, link) for:
      - merged PRs authored by USERNAME, excluding repos owned by USERNAME
      - issues authored by USERNAME, excluding repos owned by USERNAME
    """
    rows: list[tuple[str, str, str, str]] = []

    merged_prs = search_issues(f"author:{USERNAME} type:pr is:merged -user:{USERNAME}")
    for item in merged_prs:
        repo_full_name = "/".join(item["repository_url"].split("/")[-2:])
        rows.append(
            (
                repo_full_name,
                "Bug fix / PR",
                item["title"],
                f"[#{item['number']}]({item['html_url']})",
            )
        )

    opened_issues = search_issues(f"author:{USERNAME} type:issue -user:{USERNAME}")
    for item in opened_issues:
        repo_full_name = "/".join(item["repository_url"].split("/")[-2:])
        rows.append(
            (
                repo_full_name,
                "Issue",
                item["title"],
                f"[#{item['number']}]({item['html_url']})",
            )
        )

    return rows[:MAX_ROWS]


def render_table(rows: list[tuple[str, str, str, str]]) -> str:
    if not rows:
        return (
            "| Repo | Type | Description | Link |\n"
            "|---|---|---|---|\n"
            "| _(no external contributions recorded yet)_ | | | |"
        )

    lines = ["| Repo | Type | Description | Link |", "|---|---|---|---|"]
    for repo, kind, desc, link in rows:
        desc = desc.replace("|", "\\|")
        lines.append(f"| {repo} | {kind} | {desc} | {link} |")
    return "\n".join(lines)


def update_readme(table_markdown: str) -> None:
    with open(README_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    if START_MARKER not in content or END_MARKER not in content:
        sys.exit(f"Could not find {START_MARKER} / {END_MARKER} in {README_PATH}")

    before = content.split(START_MARKER)[0]
    after = content.split(END_MARKER)[1]
    new_content = f"{before}{START_MARKER}\n{table_markdown}\n{END_MARKER}{after}"

    with open(README_PATH, "w", encoding="utf-8") as f:
        f.write(new_content)


def main() -> None:
    rows = build_rows()
    table_markdown = render_table(rows)
    update_readme(table_markdown)
    print(f"Updated {README_PATH} with {len(rows)} external contribution(s).")


if __name__ == "__main__":
    main()
