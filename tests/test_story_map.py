from pathlib import Path

from click.testing import CliRunner

from pm_kit.cli import main
from pm_kit.story_map.check import run_checks
from pm_kit.story_map.io import (
    load_activities,
    load_all,
    load_stories,
    load_tasks,
    parse_frontmatter,
    slugify,
)
from pm_kit.story_map.render import (
    INCLUDED_END,
    INCLUDED_START,
    MATRIX_END,
    MATRIX_START,
    build_matrix,
    render,
)


def _init_project(tmp_path: Path) -> Path:
    project_dir = tmp_path / "proj"
    project_dir.mkdir()
    (project_dir / "project.yaml").write_text("name: test\n")
    return project_dir


def _run(runner: CliRunner, project_dir: Path, args: list[str]):
    with runner.isolated_filesystem():
        # Switch into the project dir
        result = runner.invoke(main, args, catch_exceptions=False, obj=None)
    return result


def _invoke(project_dir: Path, args: list[str], monkeypatch) -> "object":
    monkeypatch.chdir(project_dir)
    runner = CliRunner()
    return runner.invoke(main, args, catch_exceptions=False)


def test_slugify():
    assert slugify("Sign up") == "sign-up"
    assert slugify("  Enter email  ") == "enter-email"
    assert slugify("Q3 / Beta Launch!") == "q3-beta-launch"
    assert slugify("") == "untitled"


def test_add_activity_creates_file(tmp_path, monkeypatch):
    project_dir = _init_project(tmp_path)
    result = _invoke(project_dir, ["story-map", "add", "activity", "--title", "Sign up"], monkeypatch)
    assert result.exit_code == 0, result.output

    activities = load_activities(project_dir)
    assert len(activities) == 1
    a = activities[0]
    assert a.id == "ACT-001"
    assert a.title == "Sign up"
    assert a.order == 1

    path = project_dir / "story-map" / "backbone" / "ACT-001-sign-up.md"
    assert path.exists()
    fm, body = parse_frontmatter(path.read_text())
    assert fm["id"] == "ACT-001"
    assert fm["order"] == 1
    assert "## Description" in body


def test_add_activity_order_shift(tmp_path, monkeypatch):
    project_dir = _init_project(tmp_path)
    _invoke(project_dir, ["story-map", "add", "activity", "--title", "Sign up"], monkeypatch)
    _invoke(project_dir, ["story-map", "add", "activity", "--title", "Check out"], monkeypatch)
    # Insert at the front
    _invoke(
        project_dir,
        ["story-map", "add", "activity", "--title", "Land on homepage", "--order", "1"],
        monkeypatch,
    )

    activities = load_activities(project_dir)
    titles_in_order = [a.title for a in activities]
    assert titles_in_order == ["Land on homepage", "Sign up", "Check out"]
    orders = [a.order for a in activities]
    assert orders == [1, 2, 3]


def test_add_task_under_activity(tmp_path, monkeypatch):
    project_dir = _init_project(tmp_path)
    _invoke(project_dir, ["story-map", "add", "activity", "--title", "Sign up"], monkeypatch)
    _invoke(
        project_dir,
        ["story-map", "add", "task", "--title", "Enter email", "--parent", "ACT-001"],
        monkeypatch,
    )

    tasks = load_tasks(project_dir)
    assert len(tasks) == 1
    assert tasks[0].id == "TASK-001"
    assert tasks[0].parent == "ACT-001"
    assert tasks[0].order == 1


def test_add_story_full_flow(tmp_path, monkeypatch):
    project_dir = _init_project(tmp_path)
    _invoke(project_dir, ["story-map", "add", "activity", "--title", "Sign up"], monkeypatch)
    _invoke(
        project_dir,
        ["story-map", "add", "task", "--title", "Enter email", "--parent", "ACT-001"],
        monkeypatch,
    )
    _invoke(
        project_dir,
        [
            "story-map",
            "add",
            "story",
            "--title",
            "Email field accepts standard addresses",
            "--parent",
            "TASK-001",
            "--kind",
            "happy",
            "--release",
            "R1",
        ],
        monkeypatch,
    )

    stories = load_stories(project_dir)
    assert len(stories) == 1
    s = stories[0]
    assert s.id == "STORY-001"
    assert s.release == "R1"
    assert s.kind == "happy"


def test_render_builds_matrix_and_overview(tmp_path, monkeypatch):
    project_dir = _init_project(tmp_path)
    _invoke(project_dir, ["story-map", "add", "activity", "--title", "Sign up"], monkeypatch)
    _invoke(project_dir, ["story-map", "add", "activity", "--title", "Check out"], monkeypatch)
    _invoke(
        project_dir,
        ["story-map", "add", "task", "--title", "Enter email", "--parent", "ACT-001"],
        monkeypatch,
    )
    _invoke(
        project_dir,
        ["story-map", "add", "task", "--title", "Pay", "--parent", "ACT-002"],
        monkeypatch,
    )
    _invoke(
        project_dir,
        ["story-map", "add", "release", "--title", "MVP", "--id", "R1"],
        monkeypatch,
    )
    _invoke(
        project_dir,
        [
            "story-map",
            "add",
            "story",
            "--title",
            "Email happy",
            "--parent",
            "TASK-001",
            "--release",
            "R1",
        ],
        monkeypatch,
    )
    _invoke(
        project_dir,
        [
            "story-map",
            "add",
            "story",
            "--title",
            "Pay happy",
            "--parent",
            "TASK-002",
            "--release",
            "R1",
        ],
        monkeypatch,
    )
    result = _invoke(project_dir, ["story-map", "render"], monkeypatch)
    assert result.exit_code == 0, result.output

    overview = (project_dir / "story-map" / "overview.md").read_text()
    assert MATRIX_START in overview
    assert MATRIX_END in overview
    assert "ACT-001 Sign up" in overview
    assert "ACT-002 Check out" in overview
    assert "TASK-001 Enter email" in overview
    assert "STORY-001" in overview
    assert "STORY-002" in overview
    # Release row labeled as "R1 MVP"
    assert "**R1 MVP**" in overview

    release_path = list((project_dir / "story-map" / "releases").glob("R1-*.md"))[0]
    release_text = release_path.read_text()
    assert INCLUDED_START in release_text
    assert INCLUDED_END in release_text
    assert "STORY-001 — Email happy" in release_text
    assert "STORY-002 — Pay happy" in release_text


def test_render_preserves_user_content_outside_markers(tmp_path, monkeypatch):
    project_dir = _init_project(tmp_path)
    _invoke(project_dir, ["story-map", "add", "activity", "--title", "Sign up"], monkeypatch)
    _invoke(project_dir, ["story-map", "render"], monkeypatch)

    overview_path = project_dir / "story-map" / "overview.md"
    text = overview_path.read_text()
    # Inject user content in the Goal section
    text = text.replace("## Goal\n\n", "## Goal\n\nA user can sign up so that they get value.\n\n")
    overview_path.write_text(text)

    # Re-render after adding another activity
    _invoke(project_dir, ["story-map", "add", "activity", "--title", "Check out"], monkeypatch)
    _invoke(project_dir, ["story-map", "render"], monkeypatch)

    text2 = overview_path.read_text()
    assert "A user can sign up so that they get value." in text2
    assert "ACT-002 Check out" in text2


def test_check_detects_mvp_gap(tmp_path, monkeypatch):
    project_dir = _init_project(tmp_path)
    _invoke(project_dir, ["story-map", "add", "activity", "--title", "Sign up"], monkeypatch)
    _invoke(project_dir, ["story-map", "add", "activity", "--title", "Check out"], monkeypatch)
    _invoke(
        project_dir,
        ["story-map", "add", "task", "--title", "Enter email", "--parent", "ACT-001"],
        monkeypatch,
    )
    _invoke(
        project_dir,
        ["story-map", "add", "task", "--title", "Pay", "--parent", "ACT-002"],
        monkeypatch,
    )
    _invoke(
        project_dir,
        ["story-map", "add", "release", "--title", "MVP", "--id", "R1"],
        monkeypatch,
    )
    _invoke(
        project_dir,
        [
            "story-map",
            "add",
            "story",
            "--title",
            "Email happy",
            "--parent",
            "TASK-001",
            "--release",
            "R1",
        ],
        monkeypatch,
    )

    issues = run_checks(project_dir)
    codes = {i.code for i in issues}
    assert "mvp-gap" in codes  # ACT-002 has no R1 story
    assert "empty-task" in codes  # TASK-002 has no stories

    # ACT-001/TASK-001 has a happy story, so no-happy-story shouldn't fire for it
    no_happy_messages = [i for i in issues if i.code == "no-happy-story"]
    assert all("TASK-001" not in i.message for i in no_happy_messages)


def test_check_detects_orphans(tmp_path, monkeypatch):
    project_dir = _init_project(tmp_path)
    _invoke(project_dir, ["story-map", "add", "activity", "--title", "Sign up"], monkeypatch)
    _invoke(
        project_dir,
        ["story-map", "add", "task", "--title", "Enter email", "--parent", "ACT-001"],
        monkeypatch,
    )
    # Manually corrupt: change task's parent to nonexistent
    task_path = list((project_dir / "story-map" / "tasks").glob("TASK-001-*.md"))[0]
    content = task_path.read_text()
    content = content.replace("parent: ACT-001", "parent: ACT-999")
    task_path.write_text(content)

    issues = run_checks(project_dir)
    assert any(i.code == "orphan-task" for i in issues)


def test_empty_project_matrix_is_placeholder(tmp_path):
    project_dir = tmp_path / "p"
    project_dir.mkdir()
    sm = load_all(project_dir)
    assert sm.activities == []
    matrix = build_matrix(sm)
    assert "No activities" in matrix


def test_render_on_empty_project_creates_overview(tmp_path):
    project_dir = tmp_path / "p"
    project_dir.mkdir()
    render(project_dir)
    overview = (project_dir / "story-map" / "overview.md").read_text()
    assert "# Story Map" in overview
    assert MATRIX_START in overview
