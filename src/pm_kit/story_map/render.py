"""Regenerate overview.md matrix and releases/R*.md Included sections."""

from __future__ import annotations

import re
from pathlib import Path

from pm_kit.story_map.io import (
    Story,
    StoryMap,
    Task,
    load_all,
    save_release,
    story_map_dir,
)

MATRIX_START = "<!-- pm-kit:story-map:matrix-start -->"
MATRIX_END = "<!-- pm-kit:story-map:matrix-end -->"
INCLUDED_START = "<!-- pm-kit:story-map:included-start -->"
INCLUDED_END = "<!-- pm-kit:story-map:included-end -->"


def _task_cell(tasks_for_activity: list[Task]) -> str:
    if not tasks_for_activity:
        return "—"
    return "<br>".join(f"{t.id} {t.title}" for t in tasks_for_activity)


def _story_cell(story_ids: list[str]) -> str:
    return ", ".join(story_ids) if story_ids else "—"


def build_matrix(sm: StoryMap) -> str:
    if not sm.activities:
        return "_No activities yet._\n"

    activities = sm.activities  # already sorted by order
    tasks_by_activity: dict[str, list[Task]] = {a.id: [] for a in activities}
    for t in sm.tasks:
        if t.parent in tasks_by_activity:
            tasks_by_activity[t.parent].append(t)
    for lst in tasks_by_activity.values():
        lst.sort(key=lambda t: t.order)

    task_parent_of_story: dict[str, str] = {t.id: t.parent for t in sm.tasks}
    release_ids = [r.id for r in sm.releases] + ["later"]
    seen: set[str] = set()
    ordered_release_ids: list[str] = []
    for rid in release_ids:
        if rid not in seen:
            ordered_release_ids.append(rid)
            seen.add(rid)

    unscheduled_present = any(s.release == "" for s in sm.stories)

    stories_by_activity_release: dict[tuple[str, str], list[str]] = {}
    for s in sm.stories:
        activity_id = task_parent_of_story.get(s.parent)
        if activity_id is None:
            continue
        bucket = s.release if s.release else "__unscheduled__"
        stories_by_activity_release.setdefault((activity_id, bucket), []).append(s.id)

    header = "| | " + " | ".join(f"{a.id} {a.title}" for a in activities) + " |"
    sep = "|" + "|".join(["---"] * (len(activities) + 1)) + "|"
    tasks_row = "| Tasks | " + " | ".join(_task_cell(tasks_by_activity[a.id]) for a in activities) + " |"

    release_lookup = {r.id: r for r in sm.releases}
    rows = [header, sep, tasks_row]
    for rid in ordered_release_ids:
        label = rid
        if rid in release_lookup:
            label = f"**{rid} {release_lookup[rid].title}**"
        elif rid == "later":
            label = "**Later**"
        row = (
            f"| {label} | "
            + " | ".join(
                _story_cell(sorted(stories_by_activity_release.get((a.id, rid), [])))
                for a in activities
            )
            + " |"
        )
        rows.append(row)

    if unscheduled_present:
        row = (
            "| **Unscheduled** | "
            + " | ".join(
                _story_cell(sorted(stories_by_activity_release.get((a.id, "__unscheduled__"), [])))
                for a in activities
            )
            + " |"
        )
        rows.append(row)

    return "\n".join(rows) + "\n"


def build_overview_content(sm: StoryMap, existing: str | None) -> str:
    """Rebuild overview.md, preserving user-authored sections outside the matrix markers."""
    matrix = build_matrix(sm)
    matrix_block = f"{MATRIX_START}\n{matrix}{MATRIX_END}"

    if existing and MATRIX_START in existing and MATRIX_END in existing:
        pattern = re.compile(
            re.escape(MATRIX_START) + r".*?" + re.escape(MATRIX_END), re.DOTALL
        )
        return pattern.sub(matrix_block, existing)

    # Fresh scaffold
    counts = (
        f"- Activities: {len(sm.activities)}\n"
        f"- Tasks: {len(sm.tasks)}\n"
        f"- Stories: {len(sm.stories)}\n"
        f"- Releases: {len(sm.releases)}\n"
    )
    return (
        "# Story Map\n\n"
        "## Goal\n\n"
        "<!-- One sentence: who can do what, so that why. -->\n\n"
        "## Personas\n\n"
        "<!-- Primary persona(s) this map covers. -->\n\n"
        "## Summary\n\n"
        f"{counts}\n"
        "## Map\n\n"
        f"{matrix_block}\n"
    )


def _replace_included_block(body: str, block: str) -> str:
    marker_block = f"{INCLUDED_START}\n{block}{INCLUDED_END}"
    if INCLUDED_START in body and INCLUDED_END in body:
        pattern = re.compile(
            re.escape(INCLUDED_START) + r".*?" + re.escape(INCLUDED_END), re.DOTALL
        )
        return pattern.sub(marker_block, body)
    # Append under an Included section if markers missing.
    if "## Included" in body:
        return body.rstrip() + "\n\n" + marker_block + "\n"
    return body.rstrip() + "\n\n## Included\n" + marker_block + "\n"


def render_release_included(sm: StoryMap) -> dict[str, str]:
    """Build the Included block content for each release."""
    out: dict[str, str] = {}
    stories_by_release: dict[str, list[Story]] = {}
    for s in sm.stories:
        if s.release:
            stories_by_release.setdefault(s.release, []).append(s)
    for r in sm.releases:
        items = sorted(stories_by_release.get(r.id, []), key=lambda s: s.id)
        if not items:
            out[r.id] = "_(no stories assigned)_\n"
        else:
            lines = [f"- {s.id} — {s.title}" for s in items]
            out[r.id] = "\n".join(lines) + "\n"
    return out


def render(project_dir: Path) -> list[Path]:
    """Regenerate overview.md and each release's Included section. Returns written paths."""
    sm = load_all(project_dir)
    sm_dir = story_map_dir(project_dir)
    sm_dir.mkdir(parents=True, exist_ok=True)

    overview_path = sm_dir / "overview.md"
    existing = overview_path.read_text() if overview_path.exists() else None
    overview_path.write_text(build_overview_content(sm, existing))

    written = [overview_path]

    included_map = render_release_included(sm)
    for r in sm.releases:
        block = included_map.get(r.id, "")
        r.body = _replace_included_block(r.body or "", block)
        path = save_release(project_dir, r)
        written.append(path)

    return written
