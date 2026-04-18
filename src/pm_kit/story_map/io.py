"""File I/O, ID allocation, slug generation, and order management for story-map files."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Any, Literal, cast

import yaml

StoryKind = Literal["happy", "unhappy", "delightful"]
StoryPriority = Literal["must", "should", "could", "wont"]
ReleaseStatus = Literal["planned", "in-progress", "released"]

FRONTMATTER_RE = re.compile(r"\A---\n(.*?)\n---\n?(.*)\Z", re.DOTALL)


@dataclass
class Activity:
    id: str
    title: str
    order: int
    persona: str = ""
    created: str = ""
    updated: str = ""
    body: str = ""


@dataclass
class Task:
    id: str
    title: str
    parent: str
    order: int
    created: str = ""
    updated: str = ""
    body: str = ""


@dataclass
class Story:
    id: str
    title: str
    parent: str
    release: str = ""
    kind: StoryKind = "happy"
    priority: StoryPriority = "should"
    created: str = ""
    updated: str = ""
    body: str = ""


@dataclass
class Release:
    id: str
    title: str
    status: ReleaseStatus = "planned"
    target_date: str = ""
    created: str = ""
    updated: str = ""
    body: str = ""


@dataclass
class StoryMap:
    activities: list[Activity] = field(default_factory=list)
    tasks: list[Task] = field(default_factory=list)
    stories: list[Story] = field(default_factory=list)
    releases: list[Release] = field(default_factory=list)


def slugify(title: str) -> str:
    s = title.lower()
    s = re.sub(r"[^a-z0-9\s-]", "", s)
    s = re.sub(r"[\s_]+", "-", s)
    s = re.sub(r"-+", "-", s).strip("-")
    return s or "untitled"


def parse_frontmatter(text: str) -> tuple[dict[str, Any], str]:
    m = FRONTMATTER_RE.match(text)
    if not m:
        raise ValueError("File is missing frontmatter delimiters (--- ... ---)")
    parsed = yaml.safe_load(m.group(1))
    fm = cast(dict[str, Any], parsed) if isinstance(parsed, dict) else {}
    body: str = m.group(2)
    return fm, body


def _render_frontmatter(keys: list[str], fm: dict[str, Any]) -> str:
    ordered = {k: fm[k] for k in keys if k in fm}
    dumped = yaml.dump(ordered, default_flow_style=False, sort_keys=False, allow_unicode=True)
    return f"---\n{dumped}---\n"


def _today() -> str:
    return date.today().isoformat()


def story_map_dir(project_dir: Path) -> Path:
    return project_dir / "story-map"


def _dir_for(project_dir: Path, kind: str) -> Path:
    return {
        "activity": story_map_dir(project_dir) / "backbone",
        "task": story_map_dir(project_dir) / "tasks",
        "story": story_map_dir(project_dir) / "stories",
        "release": story_map_dir(project_dir) / "releases",
    }[kind]


def _id_pattern(prefix: str) -> re.Pattern[str]:
    return re.compile(rf"^{prefix}-(\d+)-")


def next_id(project_dir: Path, kind: str) -> str:
    prefix = {"activity": "ACT", "task": "TASK", "story": "STORY"}[kind]
    directory = _dir_for(project_dir, kind)
    pattern = _id_pattern(prefix)
    max_n = 0
    if directory.exists():
        for f in directory.iterdir():
            m = pattern.match(f.name)
            if m:
                max_n = max(max_n, int(m.group(1)))
    return f"{prefix}-{max_n + 1:03d}"


def next_release_id(project_dir: Path) -> str:
    directory = _dir_for(project_dir, "release")
    pattern = re.compile(r"^R(\d+)-")
    max_n = 0
    if directory.exists():
        for f in directory.iterdir():
            m = pattern.match(f.name)
            if m:
                max_n = max(max_n, int(m.group(1)))
    return f"R{max_n + 1}"


def load_activities(project_dir: Path) -> list[Activity]:
    d = _dir_for(project_dir, "activity")
    if not d.exists():
        return []
    result: list[Activity] = []
    for path in sorted(d.glob("ACT-*.md")):
        fm, body = parse_frontmatter(path.read_text())
        result.append(
            Activity(
                id=fm["id"],
                title=fm["title"],
                order=int(fm.get("order", 0)),
                persona=fm.get("persona", "") or "",
                created=str(fm.get("created", "")),
                updated=str(fm.get("updated", "")),
                body=body,
            )
        )
    result.sort(key=lambda a: a.order)
    return result


def load_tasks(project_dir: Path) -> list[Task]:
    d = _dir_for(project_dir, "task")
    if not d.exists():
        return []
    result: list[Task] = []
    for path in sorted(d.glob("TASK-*.md")):
        fm, body = parse_frontmatter(path.read_text())
        result.append(
            Task(
                id=fm["id"],
                title=fm["title"],
                parent=fm["parent"],
                order=int(fm.get("order", 0)),
                created=str(fm.get("created", "")),
                updated=str(fm.get("updated", "")),
                body=body,
            )
        )
    result.sort(key=lambda t: (t.parent, t.order))
    return result


def load_stories(project_dir: Path) -> list[Story]:
    d = _dir_for(project_dir, "story")
    if not d.exists():
        return []
    result: list[Story] = []
    for path in sorted(d.glob("STORY-*.md")):
        fm, body = parse_frontmatter(path.read_text())
        result.append(
            Story(
                id=fm["id"],
                title=fm["title"],
                parent=fm["parent"],
                release=fm.get("release", "") or "",
                kind=fm.get("kind", "happy"),
                priority=fm.get("priority", "should"),
                created=str(fm.get("created", "")),
                updated=str(fm.get("updated", "")),
                body=body,
            )
        )
    return result


def load_releases(project_dir: Path) -> list[Release]:
    d = _dir_for(project_dir, "release")
    if not d.exists():
        return []
    result: list[Release] = []
    for path in sorted(d.glob("R*-*.md")):
        fm, body = parse_frontmatter(path.read_text())
        result.append(
            Release(
                id=fm["id"],
                title=fm["title"],
                status=fm.get("status", "planned"),
                target_date=str(fm.get("target_date", "") or ""),
                created=str(fm.get("created", "")),
                updated=str(fm.get("updated", "")),
                body=body,
            )
        )
    return result


def load_all(project_dir: Path) -> StoryMap:
    return StoryMap(
        activities=load_activities(project_dir),
        tasks=load_tasks(project_dir),
        stories=load_stories(project_dir),
        releases=load_releases(project_dir),
    )


def _shift_orders(
    siblings: list[Activity] | list[Task], project_dir: Path, insert_at: int, kind: str
) -> None:
    """Shift `order` of siblings >= insert_at by +1 and persist."""
    today = _today()
    for sib in siblings:
        if sib.order >= insert_at:
            sib.order += 1
            sib.updated = today
            if kind == "activity":
                save_activity(project_dir, sib)  # type: ignore[arg-type]
            else:
                save_task(project_dir, sib)  # type: ignore[arg-type]


def _activity_path(project_dir: Path, id_: str, title: str) -> Path:
    return _dir_for(project_dir, "activity") / f"{id_}-{slugify(title)}.md"


def _task_path(project_dir: Path, id_: str, title: str) -> Path:
    return _dir_for(project_dir, "task") / f"{id_}-{slugify(title)}.md"


def _story_path(project_dir: Path, id_: str, title: str) -> Path:
    return _dir_for(project_dir, "story") / f"{id_}-{slugify(title)}.md"


def _release_path(project_dir: Path, id_: str, title: str) -> Path:
    return _dir_for(project_dir, "release") / f"{id_}-{slugify(title)}.md"


def _find_existing_path(directory: Path, id_: str) -> Path | None:
    if not directory.exists():
        return None
    for p in directory.glob(f"{id_}-*.md"):
        return p
    return None


def save_activity(project_dir: Path, a: Activity) -> Path:
    directory = _dir_for(project_dir, "activity")
    directory.mkdir(parents=True, exist_ok=True)
    existing = _find_existing_path(directory, a.id)
    path = _activity_path(project_dir, a.id, a.title)
    if existing is not None and existing != path:
        existing.unlink()
    fm = {
        "id": a.id,
        "title": a.title,
        "order": a.order,
        "persona": a.persona,
        "created": a.created or _today(),
        "updated": a.updated or _today(),
    }
    body = a.body or "\n## Description\n\n## Notes\n"
    path.write_text(_render_frontmatter(["id", "title", "order", "persona", "created", "updated"], fm) + body)
    return path


def save_task(project_dir: Path, t: Task) -> Path:
    directory = _dir_for(project_dir, "task")
    directory.mkdir(parents=True, exist_ok=True)
    existing = _find_existing_path(directory, t.id)
    path = _task_path(project_dir, t.id, t.title)
    if existing is not None and existing != path:
        existing.unlink()
    fm = {
        "id": t.id,
        "title": t.title,
        "parent": t.parent,
        "order": t.order,
        "created": t.created or _today(),
        "updated": t.updated or _today(),
    }
    body = t.body or "\n## Description\n\n## Notes\n"
    path.write_text(_render_frontmatter(["id", "title", "parent", "order", "created", "updated"], fm) + body)
    return path


def _story_body(description: str, acceptance: list[str]) -> str:
    story_section = description.strip() if description else ""
    if acceptance:
        acc_section = "\n".join(f"- {item.strip()}" for item in acceptance if item.strip())
    else:
        acc_section = ""
    return f"\n## Story\n\n{story_section}\n\n## Acceptance\n\n{acc_section}\n\n## Notes\n"


def save_story(project_dir: Path, s: Story) -> Path:
    directory = _dir_for(project_dir, "story")
    directory.mkdir(parents=True, exist_ok=True)
    existing = _find_existing_path(directory, s.id)
    path = _story_path(project_dir, s.id, s.title)
    if existing is not None and existing != path:
        existing.unlink()
    fm = {
        "id": s.id,
        "title": s.title,
        "parent": s.parent,
        "release": s.release,
        "kind": s.kind,
        "priority": s.priority,
        "created": s.created or _today(),
        "updated": s.updated or _today(),
    }
    body = s.body or _story_body("", [])
    path.write_text(
        _render_frontmatter(
            ["id", "title", "parent", "release", "kind", "priority", "created", "updated"], fm
        )
        + body
    )
    return path


def save_release(project_dir: Path, r: Release) -> Path:
    directory = _dir_for(project_dir, "release")
    directory.mkdir(parents=True, exist_ok=True)
    existing = _find_existing_path(directory, r.id)
    path = _release_path(project_dir, r.id, r.title)
    if existing is not None and existing != path:
        existing.unlink()
    fm = {
        "id": r.id,
        "title": r.title,
        "status": r.status,
        "target_date": r.target_date,
        "created": r.created or _today(),
        "updated": r.updated or _today(),
    }
    body = r.body or "\n## Goal\n\n## Included\n<!-- pm-kit:story-map:included-start -->\n<!-- pm-kit:story-map:included-end -->\n\n## Excluded (explicit)\n"
    path.write_text(_render_frontmatter(["id", "title", "status", "target_date", "created", "updated"], fm) + body)
    return path


def add_activity(project_dir: Path, title: str, order: int | None, persona: str) -> Activity:
    activities = load_activities(project_dir)
    if order is None:
        order = (max((a.order for a in activities), default=0)) + 1
    else:
        _shift_orders(activities, project_dir, order, "activity")
    a = Activity(id=next_id(project_dir, "activity"), title=title, order=order, persona=persona)
    save_activity(project_dir, a)
    return a


def add_task(project_dir: Path, title: str, parent: str, order: int | None) -> Task:
    siblings = [t for t in load_tasks(project_dir) if t.parent == parent]
    if order is None:
        order = (max((t.order for t in siblings), default=0)) + 1
    else:
        _shift_orders(siblings, project_dir, order, "task")
    t = Task(id=next_id(project_dir, "task"), title=title, parent=parent, order=order)
    save_task(project_dir, t)
    return t


def add_story(
    project_dir: Path,
    title: str,
    parent: str,
    kind: StoryKind,
    release: str,
    priority: StoryPriority,
    description: str = "",
    acceptance: list[str] | None = None,
) -> Story:
    body = _story_body(description, acceptance or [])
    s = Story(
        id=next_id(project_dir, "story"),
        title=title,
        parent=parent,
        release=release,
        kind=kind,
        priority=priority,
        body=body,
    )
    save_story(project_dir, s)
    return s


def add_release(
    project_dir: Path,
    title: str,
    id_: str | None,
    target_date: str,
    status: ReleaseStatus,
) -> Release:
    if id_ is None:
        id_ = next_release_id(project_dir)
    r = Release(id=id_, title=title, status=status, target_date=target_date)
    save_release(project_dir, r)
    return r
