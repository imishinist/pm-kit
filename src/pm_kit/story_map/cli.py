"""CLI commands for story-map."""

from __future__ import annotations

import click

from pm_kit.project import find_project_dir
from pm_kit.story_map.check import format_issues, run_checks
from pm_kit.story_map.io import (
    add_activity,
    add_release,
    add_story,
    add_task,
)
from pm_kit.story_map.render import render as render_all
from pm_kit.story_map.render import set_goal, set_personas


@click.group("story-map")
def story_map() -> None:
    """Manage a user story map under story-map/."""


@story_map.group()
def add() -> None:
    """Add a node (activity/task/story/release)."""


@add.command("activity")
@click.option("--title", required=True, help="Activity title (verb phrase, e.g. 'Sign up').")
@click.option("--order", type=int, default=None, help="Position in backbone (1-based). Default: append.")
@click.option("--persona", default="", help="Persona this activity belongs to.")
def add_activity_cmd(title: str, order: int | None, persona: str) -> None:
    """Add an Activity to the backbone."""
    project_dir = find_project_dir()
    a = add_activity(project_dir, title=title, order=order, persona=persona)
    click.echo(f"Created {a.id} '{a.title}' at order {a.order}")


@add.command("task")
@click.option("--title", required=True, help="User task title (verb phrase).")
@click.option("--parent", required=True, help="Parent Activity ID (e.g. ACT-001).")
@click.option("--order", type=int, default=None, help="Position within the Activity. Default: append.")
def add_task_cmd(title: str, parent: str, order: int | None) -> None:
    """Add a User Task under an Activity."""
    project_dir = find_project_dir()
    t = add_task(project_dir, title=title, parent=parent, order=order)
    click.echo(f"Created {t.id} '{t.title}' under {t.parent} at order {t.order}")


@add.command("story")
@click.option("--title", required=True, help="Story title.")
@click.option("--parent", required=True, help="Parent User Task ID (e.g. TASK-001).")
@click.option(
    "--kind",
    type=click.Choice(["happy", "unhappy", "delightful"]),
    default="happy",
)
@click.option("--release", default="", help="Release slice (R1, R2, later, or empty).")
@click.option(
    "--priority",
    type=click.Choice(["must", "should", "could", "wont"]),
    default="should",
)
@click.option(
    "--description",
    default="",
    help="Full user-story prose, e.g. 'As a busy individual, I want X so that Y'.",
)
@click.option(
    "--acceptance",
    default="",
    help="Acceptance criteria separated by ';' — each becomes a bullet.",
)
def add_story_cmd(
    title: str,
    parent: str,
    kind: str,
    release: str,
    priority: str,
    description: str,
    acceptance: str,
) -> None:
    """Add a Story under a User Task."""
    project_dir = find_project_dir()
    acceptance_items = [p.strip() for p in acceptance.split(";") if p.strip()]
    s = add_story(
        project_dir,
        title=title,
        parent=parent,
        kind=kind,  # type: ignore[arg-type]
        release=release,
        priority=priority,  # type: ignore[arg-type]
        description=description,
        acceptance=acceptance_items,
    )
    click.echo(f"Created {s.id} '{s.title}' under {s.parent} [{s.kind}, {s.release or 'unscheduled'}]")


@add.command("release")
@click.option("--title", required=True, help="Release title (e.g. 'MVP').")
@click.option("--id", "id_", default=None, help="Release ID (R1, R2, later). Default: next available.")
@click.option("--target-date", default="", help="Target date (YYYY-MM-DD).")
@click.option(
    "--status",
    type=click.Choice(["planned", "in-progress", "released"]),
    default="planned",
)
def add_release_cmd(title: str, id_: str | None, target_date: str, status: str) -> None:
    """Add a Release slice."""
    project_dir = find_project_dir()
    r = add_release(project_dir, title=title, id_=id_, target_date=target_date, status=status)  # type: ignore[arg-type]
    click.echo(f"Created {r.id} '{r.title}'")


@story_map.command("set-goal")
@click.argument("goal")
def set_goal_cmd(goal: str) -> None:
    """Set the one-sentence Goal in overview.md."""
    project_dir = find_project_dir()
    path = set_goal(project_dir, goal)
    click.echo(f"Updated Goal in {path.relative_to(project_dir)}")


@story_map.command("set-personas")
@click.argument("personas")
def set_personas_cmd(personas: str) -> None:
    """Set the Personas section in overview.md (free-form text; use bullet list for multiple)."""
    project_dir = find_project_dir()
    path = set_personas(project_dir, personas)
    click.echo(f"Updated Personas in {path.relative_to(project_dir)}")


@story_map.command()
def render() -> None:
    """Regenerate overview.md and releases/ Included sections."""
    project_dir = find_project_dir()
    written = render_all(project_dir)
    for p in written:
        click.echo(f"Wrote {p.relative_to(project_dir)}")


@story_map.command()
def check() -> None:
    """Run consistency checks on the story map."""
    project_dir = find_project_dir()
    issues = run_checks(project_dir)
    click.echo(format_issues(issues), nl=False)
    errors = [i for i in issues if i.severity == "error"]
    if errors:
        raise SystemExit(1)
