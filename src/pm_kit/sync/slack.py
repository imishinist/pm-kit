"""Slack sync: fetch channel messages into data/slack/."""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any

import click
import requests


def _token() -> str:
    token = os.environ.get("SLACK_BOT_TOKEN", "")
    if not token:
        raise click.ClickException("SLACK_BOT_TOKEN must be set in environment")
    return token


def _api(method: str, token: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
    resp = requests.get(
        f"https://slack.com/api/{method}",
        headers={"Authorization": f"Bearer {token}"},
        params=params or {},
        timeout=30,
    )
    resp.raise_for_status()
    data = resp.json()
    if not data.get("ok"):
        raise click.ClickException(f"Slack API error: {data.get('error', 'unknown')}")
    return data


def _resolve_channel_id(channel_name: str, token: str) -> str:
    """Resolve a channel name (e.g. #proj-foo) to a channel ID."""
    name = channel_name.lstrip("#")
    cursor = None
    while True:
        params = {"types": "public_channel,private_channel", "limit": 200}
        if cursor:
            params["cursor"] = cursor
        data = _api("conversations.list", token, params)
        for ch in data.get("channels", []):
            if ch["name"] == name:
                return ch["id"]
        cursor = data.get("response_metadata", {}).get("next_cursor")
        if not cursor:
            break
    raise click.ClickException(f"Channel not found: {channel_name}")


def _fetch_messages(channel_id: str, token: str, oldest: str | None = None) -> list[dict[str, Any]]:
    """Fetch messages from a channel, optionally since a timestamp."""
    messages: list[dict[str, Any]] = []
    cursor: str | None = None
    while True:
        params: dict[str, Any] = {"channel": channel_id, "limit": 200}
        if oldest:
            params["oldest"] = oldest
        if cursor:
            params["cursor"] = cursor
        data = _api("conversations.history", token, params)
        messages.extend(data.get("messages", []))
        cursor = data.get("response_metadata", {}).get("next_cursor")
        if not cursor:
            break
    return messages


def _fetch_replies(channel_id: str, thread_ts: str, token: str) -> list[dict[str, Any]]:
    """Fetch thread replies."""
    data = _api("conversations.replies", token, {"channel": channel_id, "ts": thread_ts})
    replies = data.get("messages", [])
    # First message is the parent, skip it
    return replies[1:] if len(replies) > 1 else []


def _ts_to_date(ts: str) -> str:
    return datetime.fromtimestamp(float(ts)).strftime("%Y-%m-%d")


def _message_to_record(msg: dict[str, Any], replies: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "ts": msg.get("ts", ""),
        "user": msg.get("user", ""),
        "text": msg.get("text", ""),
        "thread_ts": msg.get("thread_ts") if msg.get("reply_count") else None,
        "replies": [
            {"ts": r["ts"], "user": r.get("user", ""), "text": r.get("text", "")}
            for r in replies
        ],
    }


def sync_slack(project_dir: Path, config: dict[str, Any]) -> None:
    """Sync Slack channels into project_dir/data/slack/."""
    slack_config = config.get("slack")
    if not slack_config:
        raise click.ClickException("slack section not configured in project.yaml")

    channels = slack_config.get("channels", [])
    if not channels:
        raise click.ClickException("No Slack channels configured")

    token = _token()
    raw_dir = project_dir / "data" / "slack" / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)

    for channel_name in channels:
        name = channel_name.lstrip("#")
        click.echo(f"Syncing Slack channel: {channel_name}")

        channel_id = _resolve_channel_id(channel_name, token)
        channel_dir = raw_dir / name
        channel_dir.mkdir(parents=True, exist_ok=True)

        # Determine oldest timestamp for incremental sync
        oldest = None
        existing_files = sorted(channel_dir.glob("*.jsonl"))
        if existing_files:
            # Fetch from the start of the latest existing date
            latest_date = existing_files[-1].stem
            oldest = str(datetime.strptime(latest_date, "%Y-%m-%d").timestamp())

        messages = _fetch_messages(channel_id, token, oldest)
        click.echo(f"  {len(messages)} messages fetched")

        # Group messages by date
        by_date: dict[str, list[dict[str, Any]]] = {}
        for msg in messages:
            if msg.get("subtype") in ("channel_join", "channel_leave"):
                continue
            msg_date = _ts_to_date(msg["ts"])
            by_date.setdefault(msg_date, []).append(msg)

        for msg_date, day_msgs in sorted(by_date.items()):
            records: list[dict[str, Any]] = []
            for msg in sorted(day_msgs, key=lambda m: float(m["ts"])):
                replies: list[dict[str, Any]] = []
                if msg.get("reply_count", 0) > 0:
                    replies = _fetch_replies(channel_id, msg["ts"], token)
                records.append(_message_to_record(msg, replies))

            outfile = channel_dir / f"{msg_date}.jsonl"
            with outfile.open("w") as f:
                for rec in records:
                    f.write(json.dumps(rec, ensure_ascii=False) + "\n")

        click.echo(f"  Written to {channel_dir}")

    click.echo("Slack sync complete")
