"""Schema definitions for sync output JSON."""

import json
import sys

import click

JIRA_SCHEMA: dict[str, object] = {
    "type": "object",
    "properties": {
        "project_key": {"type": "string", "description": "Jira project key (e.g. RNW)"},
        "fetched_at": {"type": "string", "description": "Date of fetch (YYYY-MM-DD)"},
        "total_issues": {"type": "integer"},
        "active_issue_count": {"type": "integer"},
        "sprints": {
            "type": "array",
            "description": "All sprints (active, closed, future). Scrum boards only.",
            "items": {
                "type": "object",
                "properties": {
                    "id": {"type": "integer"},
                    "name": {"type": "string"},
                    "state": {
                        "type": "string",
                        "description": "Sprint state: active, closed, or future",
                    },
                    "start_date": {"type": "string"},
                    "end_date": {"type": "string"},
                },
            },
        },
        "tickets": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "key": {
                        "type": "string",
                        "description": "Ticket key (e.g. RNW-42)",
                    },
                    "summary": {"type": "string"},
                    "status": {"type": "string"},
                    "assignee": {"type": "string"},
                    "priority": {"type": "string"},
                    "issue_type": {"type": "string"},
                    "created": {"type": "string"},
                    "updated": {"type": "string"},
                    "active": {
                        "type": "boolean",
                        "description": "True if in active sprint or kanban in-progress",
                    },
                    "epic_key": {
                        "type": "string",
                        "description": "Epic key (e.g. RNW-10). Empty string if not linked to an epic.",
                    },
                    "epic_name": {
                        "type": "string",
                        "description": "Epic name/summary. Empty string if not linked to an epic.",
                    },
                    "description": {
                        "type": "string",
                        "description": "Present only when active=true",
                    },
                    "comments": {
                        "type": "array",
                        "description": "Present only when active=true. Raw Jira comment objects.",
                        "items": {"type": "object"},
                    },
                },
            },
        },
    },
}

SLACK_SCHEMA: dict[str, object] = {
    "type": "object",
    "properties": {
        "fetched_at": {
            "type": "string",
            "description": "Timestamp of fetch (ISO 8601)",
        },
        "channels": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "channel": {
                        "type": "string",
                        "description": "Channel name (without #)",
                    },
                    "channel_id": {"type": "string"},
                    "message_count": {"type": "integer"},
                    "messages": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "ts": {
                                    "type": "string",
                                    "description": "Message timestamp",
                                },
                                "user": {"type": "string", "description": "User ID"},
                                "text": {"type": "string"},
                                "thread_ts": {
                                    "type": ["string", "null"],
                                    "description": "Thread parent timestamp, null if not a thread",
                                },
                                "replies": {
                                    "type": "array",
                                    "items": {
                                        "type": "object",
                                        "properties": {
                                            "ts": {"type": "string"},
                                            "user": {"type": "string"},
                                            "text": {"type": "string"},
                                        },
                                    },
                                },
                            },
                        },
                    },
                },
            },
        },
    },
}

CONFLUENCE_SCHEMA: dict[str, object] = {
    "type": "object",
    "properties": {
        "space_key": {"type": "string"},
        "base_url": {"type": "string"},
        "total_pages": {"type": "integer"},
        "pages": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "id": {"type": "string", "description": "Page ID"},
                    "title": {"type": "string"},
                    "body_html": {
                        "type": "string",
                        "description": "Page body in Confluence storage format (HTML)",
                    },
                    "ancestors": {
                        "type": "array",
                        "description": "Parent pages from root to immediate parent",
                        "items": {
                            "type": "object",
                            "properties": {
                                "id": {"type": "string"},
                                "title": {"type": "string"},
                            },
                        },
                    },
                    "children": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "id": {"type": "string"},
                                "title": {"type": "string"},
                            },
                        },
                    },
                    "labels": {"type": "array", "items": {"type": "string"}},
                    "created_by": {"type": "string"},
                    "updated_at": {"type": "string"},
                    "version": {"type": "integer"},
                    "attachments": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "title": {"type": "string"},
                                "download_url": {
                                    "type": "string",
                                    "description": "Relative URL path for download",
                                },
                            },
                        },
                    },
                },
            },
        },
    },
}

SCHEMAS: dict[str, dict[str, object]] = {
    "jira": JIRA_SCHEMA,
    "slack": SLACK_SCHEMA,
    "confluence": CONFLUENCE_SCHEMA,
}


@click.command()
@click.argument("source", type=click.Choice(["jira", "slack", "confluence"]))
def schema(source: str) -> None:
    """Show the JSON schema for a sync source's output."""
    json.dump(SCHEMAS[source], sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")
