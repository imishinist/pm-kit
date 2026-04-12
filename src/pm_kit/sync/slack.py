"""Slack sync: fetch channel messages as raw JSON."""

import json
import os
import sys
from datetime import datetime
from typing import Any

import click
import requests


def _token() -> str:
    token = os.environ.get("SLACK_USER_TOKEN", "")
    if not token:
        raise click.ClickException("SLACK_USER_TOKEN must be set in environment")
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
    cursor: str | None = None
    while True:
        params: dict[str, Any] = {"types": "public_channel,private_channel", "limit": 200}
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


def fetch_slack(config: dict[str, Any], since: str | None = None) -> dict[str, Any]:
    """Fetch Slack data and return as a dict.

    Args:
        config: project.yaml config dict.
        since: fetch messages since this date (YYYY-MM-DD). None for all messages.
    """
    slack_config = config.get("slack")
    if not slack_config:
        raise click.ClickException("slack section not configured in project.yaml")

    channels_list = slack_config.get("channels", [])
    if not channels_list:
        raise click.ClickException("No Slack channels configured")

    token = _token()

    # Convert since date to Slack oldest timestamp
    oldest: str | None = None
    if since:
        oldest = str(datetime.strptime(since, "%Y-%m-%d").timestamp())

    channels: list[dict[str, Any]] = []
    for channel_name in channels_list:
        name = channel_name.lstrip("#")
        channel_id = _resolve_channel_id(channel_name, token)

        messages = _fetch_messages(channel_id, token, oldest=oldest)

        records: list[dict[str, Any]] = []
        for msg in sorted(messages, key=lambda m: float(m.get("ts", "0"))):
            if msg.get("subtype") in ("channel_join", "channel_leave"):
                continue
            replies: list[dict[str, Any]] = []
            if msg.get("reply_count", 0) > 0:
                replies = _fetch_replies(channel_id, msg["ts"], token)
            records.append(_message_to_record(msg, replies))

        channels.append({
            "channel": name,
            "channel_id": channel_id,
            "message_count": len(records),
            "messages": records,
        })

    return {
        "fetched_at": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
        "channels": channels,
    }


def sync_slack(config: dict[str, Any], since: str | None = None) -> None:
    """Fetch Slack data and output as JSON to stdout."""
    result = fetch_slack(config, since=since)
    json.dump(result, sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")
