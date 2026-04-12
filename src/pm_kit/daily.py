"""Daily check: gather synced data and produce a summary for AI analysis."""

import json
from datetime import date, timedelta
from pathlib import Path
from typing import Any

import click
import yaml


def _read_sprint_summary(jira_dir: Path) -> str | None:
    board_md = jira_dir / "board.md"
    if board_md.exists():
        return board_md.read_text()
    return None


def _read_active_tickets(jira_dir: Path) -> list[dict[str, str]]:
    """Read tickets that have detail (active tickets)."""
    tickets_dir = jira_dir / "tickets"
    if not tickets_dir.exists():
        return []

    active: list[dict[str, str]] = []
    for ticket_dir in sorted(tickets_dir.iterdir()):
        ticket_md = ticket_dir / "ticket.md"
        if not ticket_md.exists():
            continue
        content = ticket_md.read_text()
        # Active tickets have detail (a heading after frontmatter)
        if content.count("---") >= 2:
            after_frontmatter = content.split("---", 2)[2]
            if after_frontmatter.strip():
                active.append({"key": ticket_dir.name, "content": content})
    return active


def _read_recent_slack_digests(slack_dir: Path, days: int = 3) -> list[dict[str, str]]:
    """Read recent Slack digest files."""
    digest_dir = slack_dir / "digest"
    if not digest_dir.exists():
        return []

    today = date.today()
    digests: list[dict[str, str]] = []
    for i in range(days):
        d = today - timedelta(days=i)
        digest_file = digest_dir / f"{d}.md"
        if digest_file.exists():
            digests.append({"date": str(d), "content": digest_file.read_text()})
    return digests


def _read_recent_slack_raw(slack_dir: Path, days: int = 1) -> list[dict[str, Any]]:
    """Read recent raw Slack messages if no digests exist."""
    raw_dir = slack_dir / "raw"
    if not raw_dir.exists():
        return []

    today = date.today()
    messages: list[dict[str, Any]] = []
    for channel_dir in sorted(raw_dir.iterdir()):
        if not channel_dir.is_dir():
            continue
        for i in range(days):
            d = today - timedelta(days=i)
            jsonl_file = channel_dir / f"{d}.jsonl"
            if jsonl_file.exists():
                records: list[Any] = []
                for line in jsonl_file.read_text().splitlines():
                    if line.strip():
                        records.append(json.loads(line))
                messages.append(
                    {
                        "channel": channel_dir.name,
                        "date": str(d),
                        "message_count": len(records),
                        "records": records,
                    }
                )
    return messages


def _read_risk_register(project_dir: Path) -> str | None:
    risk_file = project_dir / "risks" / "risk-register.md"
    if risk_file.exists():
        return risk_file.read_text()
    return None


def _read_sprint_current(jira_dir: Path) -> str | None:
    sprint_file = jira_dir / "sprints" / "current.md"
    if sprint_file.exists():
        return sprint_file.read_text()
    return None


def gather_daily_context(project_dir: Path) -> str:
    """Gather all relevant data and produce a context document for AI analysis."""
    config_path = project_dir / "project.yaml"
    config: dict[str, Any] = (
        yaml.safe_load(config_path.read_text()) if config_path.exists() else {}
    )

    sections: list[str] = []
    sections.append(f"# Daily Check — {date.today()}")
    sections.append(f"Project: {config.get('name', 'unknown')}")
    sections.append("")

    jira_dir = project_dir / "data" / "jira"
    slack_dir = project_dir / "data" / "slack"

    # Sprint info
    sprint = _read_sprint_current(jira_dir)
    if sprint:
        sections.append("## Current Sprint")
        sections.append(sprint)
        sections.append("")

    # Board summary
    board = _read_sprint_summary(jira_dir)
    if board:
        sections.append("## Board Summary")
        sections.append(board)
        sections.append("")

    # Active tickets
    active_tickets = _read_active_tickets(jira_dir)
    if active_tickets:
        sections.append(f"## Active Tickets ({len(active_tickets)})")
        sections.append("")
        for t in active_tickets:
            sections.append(f"### {t['key']}")
            sections.append(t["content"])
            sections.append("")

    # Slack digests or raw
    digests = _read_recent_slack_digests(slack_dir)
    if digests:
        sections.append("## Slack Digest (Recent)")
        for d in digests:
            sections.append(f"### {d['date']}")
            sections.append(d["content"])
            sections.append("")
    else:
        raw = _read_recent_slack_raw(slack_dir)
        if raw:
            sections.append("## Slack Messages (Recent)")
            for r in raw:
                sections.append(
                    f"### #{r['channel']} — {r['date']} ({r['message_count']} messages)"
                )
                for rec in r["records"][:20]:  # Limit to avoid overwhelming output
                    text = rec.get("text", "")
                    user = rec.get("user", "")
                    sections.append(f"- **{user}**: {text}")
                    for reply in rec.get("replies", []):
                        sections.append(
                            f"  - **{reply.get('user', '')}**: {reply.get('text', '')}"
                        )
                sections.append("")

    # Risk register
    risks = _read_risk_register(project_dir)
    if risks:
        sections.append("## Risk Register")
        sections.append(risks)
        sections.append("")

    # Prompt
    prompt_file = project_dir / "prompts" / "daily-check.md"
    if prompt_file.exists():
        sections.append("---")
        sections.append("")
        sections.append(prompt_file.read_text())

    return "\n".join(sections)


@click.command()
def daily():
    """Run daily check: gather project data and output analysis context."""
    from pm_kit.project import find_project_dir

    project_dir = find_project_dir()
    context = gather_daily_context(project_dir)
    click.echo(context)
