import shutil
from pathlib import Path

from click.testing import CliRunner

from pm_kit.cli import main
from pm_kit.create import get_pm_kit_root


def _create_project(tmp_path, monkeypatch) -> Path:
    monkeypatch.setenv("XDG_DATA_HOME", str(tmp_path / "xdg_data"))
    project_dir = tmp_path / "my-project"
    runner = CliRunner()
    result = runner.invoke(main, ["create", "my-project", "--path", str(project_dir)])
    assert result.exit_code == 0, result.output
    return project_dir


def test_update_no_changes(tmp_path, monkeypatch):
    project_dir = _create_project(tmp_path, monkeypatch)

    runner = CliRunner()
    result = runner.invoke(main, ["update", str(project_dir)])

    assert result.exit_code == 0, result.output
    assert "up-to-date" in result.output
    assert "0 added" in result.output
    assert "0 skipped" in result.output


def test_update_modified_file_skip(tmp_path, monkeypatch):
    project_dir = _create_project(tmp_path, monkeypatch)

    # Modify a prompt file
    daily = project_dir / "prompts" / "daily-check.md"
    daily.write_text(daily.read_text() + "\n## Custom Rule\n")

    runner = CliRunner()
    result = runner.invoke(main, ["update", str(project_dir)], input="n\n")

    assert result.exit_code == 0, result.output
    assert "1 skipped" in result.output
    # File should still have custom content
    assert "## Custom Rule" in daily.read_text()


def test_update_modified_file_overwrite(tmp_path, monkeypatch):
    project_dir = _create_project(tmp_path, monkeypatch)

    daily = project_dir / "prompts" / "daily-check.md"
    daily.write_text(daily.read_text() + "\n## Custom Rule\n")

    runner = CliRunner()
    result = runner.invoke(main, ["update", str(project_dir)], input="y\n")

    assert result.exit_code == 0, result.output
    assert "updated: prompts/daily-check.md" in result.output
    # Custom content should be gone
    assert "## Custom Rule" not in daily.read_text()


def test_update_new_file_added(tmp_path, monkeypatch):
    project_dir = _create_project(tmp_path, monkeypatch)

    # Simulate a new prompt added to scaffold
    scaffold_prompts = get_pm_kit_root() / "scaffold" / "prompts"
    new_prompt = scaffold_prompts / "weekly-report.md"
    new_prompt.write_text("# Weekly Report\n")

    try:
        runner = CliRunner()
        result = runner.invoke(main, ["update", str(project_dir)])

        assert result.exit_code == 0, result.output
        assert "added: prompts/weekly-report.md" in result.output
        assert (project_dir / "prompts" / "weekly-report.md").is_file()
    finally:
        new_prompt.unlink()


def test_update_no_prompts_dir(tmp_path, monkeypatch):
    project_dir = _create_project(tmp_path, monkeypatch)

    # Remove prompts directory
    shutil.rmtree(project_dir / "prompts")

    runner = CliRunner()
    result = runner.invoke(main, ["update", str(project_dir)])

    assert result.exit_code == 0, result.output
    assert "Copying from scaffold" in result.output
    assert (project_dir / "prompts" / "system.md").is_file()


def test_update_skills_modified(tmp_path, monkeypatch):
    project_dir = _create_project(tmp_path, monkeypatch)

    # Modify a skill file
    skill = project_dir / "skills" / "sync-jira.md"
    skill.write_text(skill.read_text() + "\n## Custom Step\n")

    runner = CliRunner()
    result = runner.invoke(main, ["update", str(project_dir)], input="n\n")

    assert result.exit_code == 0, result.output
    assert "1 skipped" in result.output
    assert "## Custom Step" in skill.read_text()


def test_update_skills_no_dir(tmp_path, monkeypatch):
    project_dir = _create_project(tmp_path, monkeypatch)

    shutil.rmtree(project_dir / "skills")

    runner = CliRunner()
    result = runner.invoke(main, ["update", str(project_dir)])

    assert result.exit_code == 0, result.output
    assert "Copying from scaffold" in result.output
    assert (project_dir / "skills" / "sync-jira.md").is_file()
