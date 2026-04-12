"""Jira sync: fetch tickets and sprints into data/jira/."""

import json
import os
from datetime import date, timedelta
from pathlib import Path

import click
import requests
import yaml


def _auth() -> tuple[str, str]:
    user = os.environ.get("JIRA_USER", "")
    token = os.environ.get("JIRA_API_TOKEN", "")
    if not user or not token:
        raise click.ClickException("JIRA_USER and JIRA_API_TOKEN must be set in environment")
    return user, token


def _get(url: str, auth: tuple[str, str], params: dict | None = None) -> dict:
    resp = requests.get(url, auth=auth, params=params or {}, timeout=30)
    resp.raise_for_status()
    return resp.json()


def _ticket_frontmatter(issue: dict) -> dict:
    fields = issue["fields"]
    return {
        "key": issue["key"],
        "summary": fields.get("summary", ""),
        "status": fields.get("status", {}).get("name", ""),
        "assignee": (fields.get("assignee") or {}).get("displayName", ""),
        "priority": (fields.get("priority") or {}).get("name", ""),
        "issue_type": (fields.get("issuetype") or {}).get("name", ""),
        "created": fields.get("created", ""),
        "updated": fields.get("updated", ""),
    }


def _render_ticket_md(issue: dict, detail: bool) -> str:
    fm = _ticket_frontmatter(issue)
    lines = ["---"]
    lines += [f"{k}: {json.dumps(v, ensure_ascii=False)}" for k, v in fm.items()]
    lines += ["---", ""]

    if detail:
        fields = issue["fields"]
        lines.append(f"# {fm['key']}: {fm['summary']}")
        lines.append("")
        description = fields.get("description") or "(no description)"
        lines.append(description)
        lines.append("")

    return "\n".join(lines)


def _render_comments_md(comments: list[dict]) -> str:
    lines = ["# Comments", ""]
    for c in comments:
        author = c.get("author", {}).get("displayName", "unknown")
        created = c.get("created", "")
        body = c.get("body", "")
        lines.append(f"## {author} ({created})")
        lines.append("")
        lines.append(body)
        lines.append("")
    return "\n".join(lines)


def _fetch_all_issues(base_url: str, project_key: str, auth: tuple[str, str], updated_since: str | None = None) -> list[dict]:
    jql = f"project = {project_key}"
    if updated_since:
        jql += f' AND updated >= "{updated_since}"'
    jql += " ORDER BY updated DESC"

    issues: list[dict] = []
    start_at = 0
    max_results = 50

    while True:
        data = _get(
            f"{base_url}/rest/api/2/search",
            auth,
            {"jql": jql, "startAt": start_at, "maxResults": max_results},
        )
        issues.extend(data.get("issues", []))
        if start_at + max_results >= data.get("total", 0):
            break
        start_at += max_results

    return issues


def _fetch_comments(base_url: str, issue_key: str, auth: tuple[str, str]) -> list[dict]:
    data = _get(f"{base_url}/rest/api/2/issue/{issue_key}/comment", auth)
    return data.get("comments", [])


def _get_active_sprint_issue_keys(base_url: str, board_id: int, auth: tuple[str, str]) -> set[str]:
    """Get issue keys in the active sprint."""
    data = _get(f"{base_url}/rest/agile/1.0/board/{board_id}/sprint", auth, {"state": "active"})
    sprints = data.get("values", [])
    if not sprints:
        return set()

    sprint = sprints[0]
    sprint_issues = _get(
        f"{base_url}/rest/agile/1.0/sprint/{sprint['id']}/issue",
        auth,
        {"maxResults": 200},
    )

    keys = {i["key"] for i in sprint_issues.get("issues", [])}

    # Write sprint summary
    return keys


def _get_kanban_active_issue_keys(base_url: str, board_id: int, auth: tuple[str, str]) -> set[str]:
    """Get issue keys on kanban board that are not in backlog and not done."""
    data = _get(
        f"{base_url}/rest/agile/1.0/board/{board_id}/issue",
        auth,
        {"maxResults": 200},
    )
    keys = set()
    for issue in data.get("issues", []):
        status_cat = issue["fields"].get("status", {}).get("statusCategory", {}).get("key", "")
        # Skip 'new' (TODO/Backlog) — include in-progress and others except done
        if status_cat not in ("new", "done"):
            keys.add(issue["key"])
    return keys


def _write_sprint_info(base_url: str, board_id: int, auth: tuple[str, str], jira_dir: Path) -> None:
    """Write current sprint info to sprints/current.md."""
    data = _get(f"{base_url}/rest/agile/1.0/board/{board_id}/sprint", auth, {"state": "active"})
    sprints = data.get("values", [])
    if not sprints:
        return

    sprint = sprints[0]
    sprints_dir = jira_dir / "sprints"
    sprints_dir.mkdir(parents=True, exist_ok=True)

    lines = [
        "---",
        f"id: {sprint['id']}",
        f"name: {json.dumps(sprint.get('name', ''), ensure_ascii=False)}",
        f"state: {sprint.get('state', '')}",
        f"start_date: {sprint.get('startDate', '')}",
        f"end_date: {sprint.get('endDate', '')}",
        "---",
        "",
        f"# {sprint.get('name', 'Current Sprint')}",
        "",
    ]
    (sprints_dir / "current.md").write_text("\n".join(lines))


def sync_jira(project_dir: Path, config: dict) -> None:
    """Sync Jira data into project_dir/data/jira/."""
    jira_config = config.get("jira")
    if not jira_config:
        raise click.ClickException("jira section not configured in project.yaml")

    base_url = jira_config.get("url") or os.environ.get("JIRA_URL", "")
    if not base_url:
        raise click.ClickException("Jira URL not configured (project.yaml or JIRA_URL env)")

    project_key = jira_config["project_key"]
    board_id = jira_config.get("board_id")
    board_type = jira_config.get("board_type", "scrum")
    auth = _auth()

    jira_dir = project_dir / "data" / "jira"
    tickets_dir = jira_dir / "tickets"
    tickets_dir.mkdir(parents=True, exist_ok=True)

    # Determine active issue keys (detail + comments)
    active_keys: set[str] = set()
    if board_id:
        if board_type == "scrum":
            active_keys = _get_active_sprint_issue_keys(base_url, board_id, auth)
            _write_sprint_info(base_url, board_id, auth, jira_dir)
        elif board_type == "kanban":
            active_keys = _get_kanban_active_issue_keys(base_url, board_id, auth)

    # Check for incremental sync
    updated_since = None
    board_md = jira_dir / "board.md"
    if board_md.exists():
        # Incremental: last 7 days
        updated_since = (date.today() - timedelta(days=7)).strftime("%Y-%m-%d")

    click.echo(f"Fetching issues for {project_key}...")
    issues = _fetch_all_issues(base_url, project_key, auth, updated_since)
    click.echo(f"  {len(issues)} issues fetched")

    for issue in issues:
        key = issue["key"]
        is_active = key in active_keys
        ticket_dir = tickets_dir / key
        ticket_dir.mkdir(parents=True, exist_ok=True)

        (ticket_dir / "ticket.md").write_text(_render_ticket_md(issue, detail=is_active))

        if is_active:
            comments = _fetch_comments(base_url, key, auth)
            (ticket_dir / "comments.md").write_text(_render_comments_md(comments))

    # Write board summary
    summary_lines = [
        f"# {project_key} Board",
        "",
        f"Last synced: {date.today()}",
        f"Total issues fetched: {len(issues)}",
        f"Active issues (detail): {len(active_keys)}",
        "",
    ]
    board_md.write_text("\n".join(summary_lines))

    click.echo(f"Jira sync complete: {jira_dir}")
