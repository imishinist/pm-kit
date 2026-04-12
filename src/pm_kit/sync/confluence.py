"""Confluence sync: fetch space pages into data/confluence/."""

import os
import re
from pathlib import Path
from typing import Any

import click
import requests
import yaml


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


def _download(url: str, auth: tuple[str, str], dest: Path) -> None:
    resp = requests.get(url, auth=auth, stream=True, timeout=60)
    resp.raise_for_status()
    with dest.open("wb") as f:
        for chunk in resp.iter_content(chunk_size=8192):
            f.write(chunk)


def _slugify(title: str) -> str:
    slug = re.sub(r"[^\w\s-]", "", title.lower())
    return re.sub(r"[\s_]+", "-", slug).strip("-")


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


def _build_breadcrumb(page: dict[str, Any]) -> str:
    ancestors = page.get("ancestors", [])
    parts = [a["title"] for a in ancestors]
    parts.append(page["title"])
    return " > ".join(parts)


def _render_page_md(page: dict[str, Any]) -> str:
    breadcrumb = _build_breadcrumb(page)
    body_html = page.get("body", {}).get("storage", {}).get("value", "")
    # Store raw HTML — converting to markdown is a separate concern
    lines = [
        f"<!-- breadcrumb: {breadcrumb} -->",
        f"# {page['title']}",
        "",
        body_html,
        "",
    ]
    return "\n".join(lines)


def _build_meta(page: dict[str, Any]) -> dict[str, Any]:
    ancestors = page.get("ancestors", [])
    children = page.get("children", {}).get("page", {}).get("results", [])
    labels = page.get("metadata", {}).get("labels", {}).get("results", [])
    version = page.get("version", {})

    return {
        "id": page["id"],
        "title": page["title"],
        "parent": ancestors[-1]["id"] if ancestors else None,
        "children": [c["id"] for c in children],
        "labels": [la["name"] for la in labels],
        "created_by": version.get("by", {}).get("displayName", ""),
        "updated_at": version.get("when", ""),
        "version": version.get("number", 1),
    }


def sync_confluence(project_dir: Path, config: dict[str, Any]) -> None:
    """Sync Confluence space into project_dir/data/confluence/."""
    conf_config = config.get("confluence")
    if not conf_config:
        raise click.ClickException("confluence section not configured in project.yaml")

    base_url = conf_config.get("url") or os.environ.get("CONFLUENCE_URL", "")
    if not base_url:
        raise click.ClickException("Confluence URL not configured (project.yaml or CONFLUENCE_URL env)")

    space_key = conf_config["space_key"]
    auth = _auth()

    confluence_dir = project_dir / "data" / "confluence"
    pages_dir = confluence_dir / "pages"
    pages_dir.mkdir(parents=True, exist_ok=True)

    click.echo(f"Fetching pages from space {space_key}...")
    pages = _fetch_all_pages(base_url, space_key, auth)
    click.echo(f"  {len(pages)} pages fetched")

    index_entries: list[str] = []

    for page in pages:
        page_id = page["id"]
        slug = _slugify(page["title"])
        page_dir_name = f"{page_id}-{slug}"
        page_dir = pages_dir / page_dir_name
        page_dir.mkdir(parents=True, exist_ok=True)

        # page.md
        (page_dir / "page.md").write_text(_render_page_md(page))

        # meta.yaml
        meta = _build_meta(page)
        (page_dir / "meta.yaml").write_text(
            yaml.dump(meta, default_flow_style=False, allow_unicode=True)
        )

        # Attachments
        attachments = _fetch_attachments(base_url, page_id, auth)
        if attachments:
            att_dir = page_dir / "attachments"
            att_dir.mkdir(exist_ok=True)
            for att in attachments:
                download_url = base_url + att["_links"]["download"]
                dest = att_dir / att["title"]
                _download(download_url, auth, dest)

        breadcrumb = _build_breadcrumb(page)
        index_entries.append(f"- [{page['title']}](pages/{page_dir_name}/page.md) — {breadcrumb}")

    # index.md
    index_lines = [f"# {space_key} — Page Index", "", f"Total: {len(pages)} pages", ""]
    index_lines.extend(sorted(index_entries))
    (confluence_dir / "index.md").write_text("\n".join(index_lines) + "\n")

    click.echo(f"Confluence sync complete: {confluence_dir}")
