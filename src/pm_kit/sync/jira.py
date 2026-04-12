"""Jira sync: fetch tickets and sprints as raw JSON."""

import json
import os
import sys
from datetime import date
from typing import Any

import click
import requests


def _auth() -> tuple[str, str]:
    user = os.environ.get("JIRA_USER", "")
    token = os.environ.get("JIRA_API_TOKEN", "")
    if not user or not token:
        raise click.ClickException("JIRA_USER and JIRA_API_TOKEN must be set in environment")
    return user, token


def _get(url: str, auth: tuple[str, str], params: dict[str, Any] | None = None) -> dict[str, Any]:
    resp = requests.get(url, auth=auth, params=params or {}, timeout=30)
    resp.raise_for_status()
    return resp.json()


def _fetch_all_issues(base_url: str, project_key: str, auth: tuple[str, str], updated_since: str | None = None) -> list[dict[str, Any]]:
    jql = f"project = {project_key}"
    if updated_since:
        jql += f' AND updated >= "{updated_since}"'
    jql += " ORDER BY updated DESC"

    issues: list[dict[str, Any]] = []
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


def _fetch_comments(base_url: str, issue_key: str, auth: tuple[str, str]) -> list[dict[str, Any]]:
    data = _get(f"{base_url}/rest/api/2/issue/{issue_key}/comment", auth)
    return data.get("comments", [])


def _fetch_sprints(base_url: str, board_id: int, auth: tuple[str, str]) -> list[dict[str, Any]]:
    """Fetch all sprints (active, closed, future) for a board."""
    sprints: list[dict[str, Any]] = []
    start_at = 0
    max_results = 50

    while True:
        data = _get(
            f"{base_url}/rest/agile/1.0/board/{board_id}/sprint",
            auth,
            {"state": "active,closed,future", "startAt": start_at, "maxResults": max_results},
        )
        sprints.extend(data.get("values", []))
        if data.get("isLast", True):
            break
        start_at += max_results

    return sprints


def _get_sprint_issue_keys(base_url: str, sprint_id: int, auth: tuple[str, str]) -> set[str]:
    """Get issue keys in a sprint."""
    sprint_issues = _get(
        f"{base_url}/rest/agile/1.0/sprint/{sprint_id}/issue",
        auth,
        {"maxResults": 200},
    )
    return {i["key"] for i in sprint_issues.get("issues", [])}


def _get_kanban_active_issue_keys(base_url: str, board_id: int, auth: tuple[str, str]) -> set[str]:
    """Get issue keys on kanban board that are not in backlog and not done."""
    data = _get(
        f"{base_url}/rest/agile/1.0/board/{board_id}/issue",
        auth,
        {"maxResults": 200},
    )
    keys: set[str] = set()
    for issue in data.get("issues", []):
        fields: dict[str, Any] = issue["fields"]
        status_cat: str = fields.get("status", {}).get("statusCategory", {}).get("key", "")
        if status_cat not in ("new", "done"):
            keys.add(issue["key"])
    return keys


def _extract_issue(issue: dict[str, Any], active: bool) -> dict[str, Any]:
    """Extract relevant fields from a Jira issue."""
    fields: dict[str, Any] = issue["fields"]
    status: dict[str, Any] = fields.get("status") or {}
    assignee: dict[str, Any] = fields.get("assignee") or {}
    priority: dict[str, Any] = fields.get("priority") or {}
    issue_type: dict[str, Any] = fields.get("issuetype") or {}

    # Epic info: try common field names
    epic: dict[str, Any] = fields.get("epic") or {}
    epic_key: str = epic.get("key", "")
    epic_name: str = epic.get("name", "")
    # Fallback: parent link (Jira next-gen / Team-managed)
    if not epic_key:
        parent: dict[str, Any] = fields.get("parent") or {}
        parent_fields: dict[str, Any] = parent.get("fields") or {}
        parent_issuetype: dict[str, Any] = parent_fields.get("issuetype") or {}
        if parent_issuetype.get("name", "") == "Epic":
            epic_key = parent.get("key", "")
            epic_name = parent_fields.get("summary", "")

    result: dict[str, Any] = {
        "key": issue["key"],
        "summary": fields.get("summary", ""),
        "status": status.get("name", ""),
        "assignee": assignee.get("displayName", ""),
        "priority": priority.get("name", ""),
        "issue_type": issue_type.get("name", ""),
        "created": fields.get("created", ""),
        "updated": fields.get("updated", ""),
        "active": active,
        "epic_key": epic_key,
        "epic_name": epic_name,
    }

    if active:
        result["description"] = fields.get("description") or ""

    return result


def fetch_jira(config: dict[str, Any], since: str | None = None) -> dict[str, Any]:
    """Fetch Jira data and return as a dict.

    Args:
        config: project.yaml config dict.
        since: fetch tickets updated since this date (YYYY-MM-DD). None for all tickets.
    """
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

    # Fetch sprints and determine active issue keys
    active_keys: set[str] = set()
    sprints: list[dict[str, Any]] = []

    if board_id:
        if board_type == "scrum":
            raw_sprints = _fetch_sprints(base_url, board_id, auth)
            for s in raw_sprints:
                sprints.append({
                    "id": s["id"],
                    "name": s.get("name", ""),
                    "state": s.get("state", ""),
                    "start_date": s.get("startDate", ""),
                    "end_date": s.get("endDate", ""),
                })
                if s.get("state") == "active":
                    active_keys = _get_sprint_issue_keys(base_url, s["id"], auth)
        elif board_type == "kanban":
            active_keys = _get_kanban_active_issue_keys(base_url, board_id, auth)

    # Fetch issues
    issues = _fetch_all_issues(base_url, project_key, auth, updated_since=since)

    # Build result
    tickets: list[dict[str, Any]] = []
    for issue in issues:
        key = issue["key"]
        is_active = key in active_keys
        ticket = _extract_issue(issue, is_active)

        if is_active:
            ticket["comments"] = _fetch_comments(base_url, key, auth)

        tickets.append(ticket)

    result: dict[str, Any] = {
        "project_key": project_key,
        "fetched_at": str(date.today()),
        "total_issues": len(tickets),
        "active_issue_count": len(active_keys),
        "tickets": tickets,
    }

    if sprints:
        result["sprints"] = sprints

    return result


def sync_jira(config: dict[str, Any], since: str | None = None) -> None:
    """Fetch Jira data and output as JSON to stdout."""
    result = fetch_jira(config, since=since)
    json.dump(result, sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")
