"""Confluence sync: fetch space pages as raw JSON."""

import json
import os
import sys
from typing import Any

import click
import requests


def _auth() -> tuple[str, str]:
    user = os.environ.get("CONFLUENCE_USER", "")
    token = os.environ.get("CONFLUENCE_API_TOKEN", "")
    if not user or not token:
        raise click.ClickException("CONFLUENCE_USER and CONFLUENCE_API_TOKEN must be set in environment")
    return user, token


def _get(url: str, auth: tuple[str, str], params: dict[str, Any] | None = None) -> dict[str, Any]:
    resp = requests.get(url, auth=auth, params=params or {}, timeout=30)
    resp.raise_for_status()
    return resp.json()


def _fetch_all_pages(base_url: str, space_key: str, auth: tuple[str, str]) -> list[dict[str, Any]]:
    pages: list[dict[str, Any]] = []
    start = 0
    limit = 25

    while True:
        data = _get(
            f"{base_url}/rest/api/content",
            auth,
            {
                "spaceKey": space_key,
                "type": "page",
                "expand": "body.storage,ancestors,children.page,version,metadata.labels",
                "start": start,
                "limit": limit,
            },
        )
        pages.extend(data.get("results", []))
        if data.get("size", 0) < limit:
            break
        start += limit

    return pages


def _fetch_attachments(base_url: str, page_id: str, auth: tuple[str, str]) -> list[dict[str, Any]]:
    data = _get(
        f"{base_url}/rest/api/content/{page_id}/child/attachment",
        auth,
        {"limit": 100},
    )
    return data.get("results", [])


def _extract_page(page: dict[str, Any], attachments: list[dict[str, Any]]) -> dict[str, Any]:
    """Extract relevant fields from a Confluence page."""
    ancestors = page.get("ancestors", [])
    children = page.get("children", {}).get("page", {}).get("results", [])
    labels = page.get("metadata", {}).get("labels", {}).get("results", [])
    version = page.get("version", {})
    body_html = page.get("body", {}).get("storage", {}).get("value", "")

    return {
        "id": page["id"],
        "title": page["title"],
        "body_html": body_html,
        "ancestors": [{"id": a["id"], "title": a["title"]} for a in ancestors],
        "children": [{"id": c["id"], "title": c.get("title", "")} for c in children],
        "labels": [la["name"] for la in labels],
        "created_by": version.get("by", {}).get("displayName", ""),
        "updated_at": version.get("when", ""),
        "version": version.get("number", 1),
        "attachments": [
            {
                "title": att["title"],
                "download_url": att["_links"]["download"],
            }
            for att in attachments
        ],
    }


def fetch_confluence(config: dict[str, Any]) -> dict[str, Any]:
    """Fetch Confluence data and return as a dict."""
    conf_config = config.get("confluence")
    if not conf_config:
        raise click.ClickException("confluence section not configured in project.yaml")

    base_url = conf_config.get("url") or os.environ.get("CONFLUENCE_URL", "")
    if not base_url:
        raise click.ClickException("Confluence URL not configured (project.yaml or CONFLUENCE_URL env)")

    space_key = conf_config["space_key"]
    auth = _auth()

    raw_pages = _fetch_all_pages(base_url, space_key, auth)

    pages: list[dict[str, Any]] = []
    for page in raw_pages:
        attachments = _fetch_attachments(base_url, page["id"], auth)
        pages.append(_extract_page(page, attachments))

    return {
        "space_key": space_key,
        "base_url": base_url,
        "total_pages": len(pages),
        "pages": pages,
    }


def sync_confluence(config: dict[str, Any]) -> None:
    """Fetch Confluence data and output as JSON to stdout."""
    result = fetch_confluence(config)
    json.dump(result, sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")
