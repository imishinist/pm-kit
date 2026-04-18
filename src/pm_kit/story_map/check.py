"""Consistency checks for story-map."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from pm_kit.story_map.io import Story, Task, load_all

Severity = Literal["error", "warning"]


@dataclass
class Issue:
    severity: Severity
    code: str
    message: str


def run_checks(project_dir: Path) -> list[Issue]:
    sm = load_all(project_dir)
    issues: list[Issue] = []

    activity_ids = {a.id for a in sm.activities}
    task_ids = {t.id for t in sm.tasks}
    release_ids = {r.id for r in sm.releases}

    # Orphan references
    for t in sm.tasks:
        if t.parent not in activity_ids:
            issues.append(
                Issue("error", "orphan-task", f"{t.id} references missing parent {t.parent}")
            )
    for s in sm.stories:
        if s.parent not in task_ids:
            issues.append(
                Issue("error", "orphan-story", f"{s.id} references missing parent {s.parent}")
            )
        if s.release and s.release != "later" and s.release not in release_ids:
            issues.append(
                Issue(
                    "error",
                    "unknown-release",
                    f"{s.id} references unknown release {s.release}",
                )
            )

    # Empty nodes
    tasks_by_activity: dict[str, list[Task]] = {a.id: [] for a in sm.activities}
    for t in sm.tasks:
        if t.parent in tasks_by_activity:
            tasks_by_activity[t.parent].append(t)
    for a in sm.activities:
        if not tasks_by_activity[a.id]:
            issues.append(
                Issue("warning", "empty-activity", f"{a.id} {a.title} has no tasks")
            )

    stories_by_task: dict[str, list[Story]] = {t.id: [] for t in sm.tasks}
    for s in sm.stories:
        if s.parent in stories_by_task:
            stories_by_task[s.parent].append(s)
    for t in sm.tasks:
        if not stories_by_task[t.id]:
            issues.append(Issue("warning", "empty-task", f"{t.id} {t.title} has no stories"))
        elif not any(s.kind == "happy" for s in stories_by_task[t.id]):
            issues.append(
                Issue("warning", "no-happy-story", f"{t.id} {t.title} has no happy story")
            )

    # Duplicate titles (normalized): activities globally; tasks/stories within parent
    def _norm(s: str) -> str:
        return " ".join(s.lower().split())

    activity_titles: dict[str, list[str]] = {}
    for a in sm.activities:
        activity_titles.setdefault(_norm(a.title), []).append(a.id)
    for title_key, ids in activity_titles.items():
        if len(ids) > 1:
            issues.append(
                Issue(
                    "warning",
                    "duplicate-activity-title",
                    f"Activities {', '.join(ids)} share the title '{title_key}'",
                )
            )

    task_titles: dict[tuple[str, str], list[str]] = {}
    for t in sm.tasks:
        task_titles.setdefault((t.parent, _norm(t.title)), []).append(t.id)
    for (parent, title_key), ids in task_titles.items():
        if len(ids) > 1:
            issues.append(
                Issue(
                    "warning",
                    "duplicate-task-title",
                    f"Tasks {', '.join(ids)} under {parent} share the title '{title_key}'",
                )
            )

    story_titles: dict[tuple[str, str], list[str]] = {}
    for s in sm.stories:
        story_titles.setdefault((s.parent, _norm(s.title)), []).append(s.id)
    for (parent, title_key), ids in story_titles.items():
        if len(ids) > 1:
            issues.append(
                Issue(
                    "warning",
                    "duplicate-story-title",
                    f"Stories {', '.join(ids)} under {parent} share the title '{title_key}'",
                )
            )

    # MVP completeness: every Activity should have at least one R1 story
    if "R1" in release_ids:
        task_parent_of_story = {t.id: t.parent for t in sm.tasks}
        r1_activities: set[str] = set()
        for s in sm.stories:
            if s.release == "R1":
                activity_id = task_parent_of_story.get(s.parent)
                if activity_id:
                    r1_activities.add(activity_id)
        for a in sm.activities:
            if a.id not in r1_activities:
                issues.append(
                    Issue(
                        "warning",
                        "mvp-gap",
                        f"{a.id} {a.title} has no story scheduled in R1 — user cannot complete this phase in MVP",
                    )
                )

    return issues


def format_issues(issues: list[Issue]) -> str:
    if not issues:
        return "OK — no issues found.\n"
    lines: list[str] = []
    for issue in issues:
        lines.append(f"[{issue.severity}] {issue.code}: {issue.message}")
    return "\n".join(lines) + "\n"
