"""
Fetch this user's own public, non-fork repositories and rewrite the table
between the OWN-PROJECTS markers in README.md.

This is deliberately separate from update_external_contributions.py:
that script tracks contributions to other people's repositories, while this
script tracks repositories owned by the profile owner. Keeping the tables
separate preserves the README's honesty distinction.
"""

import os
import sys
from pathlib import Path

import requests

README_PATH = "README.md"
START_MARKER = "<!-- OWN-PROJECTS:START -->"
END_MARKER = "<!-- OWN-PROJECTS:END -->"
MAX_ROWS = 10

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


def fetch_own_repos() -> list[dict]:
    """Fetch owned public repos, most recently pushed first, excluding forks/self."""
    url = f"https://api.github.com/users/{USERNAME}/repos"
    resp = requests.get(
        url,
        headers=HEADERS,
        params={
            "sort": "pushed",
            "direction": "desc",
            "per_page": 100,
            "type": "owner",
        },
        timeout=30,
    )

    if resp.status_code == 403 and "rate limit" in resp.text.lower():
        sys.exit(
            "GitHub API rate limit hit. Make sure GH_TOKEN is passed to the script."
        )
    if resp.status_code == 404:
        sys.exit(f"GitHub user '{USERNAME}' not found (404). Check GH_USERNAME.")
    if not resp.ok:
        sys.exit(f"GitHub API request failed ({resp.status_code}):\n{resp.text}")

    repos = resp.json()
    if not isinstance(repos, list):
        sys.exit(f"Unexpected API response shape: {repos!r}")

    filtered = [
        repo
        for repo in repos
        if not repo.get("fork")
        and repo.get("name", "").lower() != USERNAME.lower()
        and repo.get("visibility", "public") == "public"
    ]
    return filtered[:MAX_ROWS]


def escape_markdown(value: str) -> str:
    return value.replace("|", "\\|").replace("\r", " ").replace("\n", " ").strip()


def render_table(repos: list[dict]) -> str:
    if not repos:
        return (
            "| Repo | Description | Last Updated | Link |\n"
            "|---|---|---|---|\n"
            "| _(no public repositories found yet)_ | | | |"
        )

    lines = [
        "| Repo | Description | Last Updated | Link |",
        "|---|---|---|---|",
    ]
    for repo in repos:
        name = escape_markdown(repo.get("name", "unknown"))
        description = escape_markdown(repo.get("description") or "") or "_no description_"
        updated = escape_markdown((repo.get("pushed_at") or "")[:10])
        link = repo.get("html_url", "")
        lines.append(f"| {name} | {description} | {updated} | [Repo]({link}) |")
    return "\n".join(lines)


def update_readme(table_markdown: str) -> None:
    """Replace exactly one marker pair and abort safely on malformed README."""
    path = Path(README_PATH)
    content = path.read_text(encoding="utf-8")

    start_count = content.count(START_MARKER)
    end_count = content.count(END_MARKER)

    if start_count == 0 or end_count == 0:
        sys.exit(
            f"Could not find {START_MARKER} / {END_MARKER} in {README_PATH}; "
            "aborting without writing."
        )
    if start_count != 1 or end_count != 1:
        sys.exit(
            f"Found duplicate markers in {README_PATH} "
            f"({start_count} START, {end_count} END); "
            "aborting without writing."
        )

    start_idx = content.index(START_MARKER)
    end_idx = content.index(END_MARKER)
    if end_idx < start_idx:
        sys.exit(
            f"END marker appears before START marker in {README_PATH}; "
            "aborting without writing."
        )

    before = content[:start_idx]
    after = content[end_idx + len(END_MARKER):]
    new_content = f"{before}{START_MARKER}\n{table_markdown}\n{END_MARKER}{after}"

    if len(new_content) < len(content) * 0.5:
        sys.exit(
            "Safety check failed: new README would be less than half the size "
            "of the original. Aborting without writing."
        )

    path.write_text(new_content, encoding="utf-8")


def main() -> None:
    repos = fetch_own_repos()
    update_readme(render_table(repos))
    print(f"Updated {README_PATH} with {len(repos)} own repo(s).")


if __name__ == "__main__":
    main()
