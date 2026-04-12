from pathlib import Path

from click.testing import CliRunner

from pm_kit.adapter.claude import generate_claude_config
from pm_kit.adapter.kiro import generate_kiro_config
from pm_kit.cli import main
from pm_kit.create import get_pm_kit_root


def _setup_project(tmp_path, monkeypatch):
    pm_kit_root = get_pm_kit_root()
    (tmp_path / "project.yaml").write_text(
        f'name: "billing"\ndescription: "Billing system"\npm_kit_path: "{pm_kit_root}"\n'
    )
    prompts_dir = tmp_path / "prompts"
    prompts_dir.mkdir()
    (prompts_dir / "system.md").write_text("# System\n")
    (prompts_dir / "daily-check.md").write_text("# Daily\n")
    monkeypatch.chdir(tmp_path)
    return tmp_path


class TestClaudeAdapter:
    def test_generates_claude_md(self, tmp_path, monkeypatch):
        project_dir = _setup_project(tmp_path, monkeypatch)
        created = generate_claude_config(project_dir)
        assert "CLAUDE.md" in created
        content = (project_dir / "CLAUDE.md").read_text()
        assert "billing" in content
        assert "pm-kit" in content

    def test_claude_md_includes_prompts(self, tmp_path, monkeypatch):
        project_dir = _setup_project(tmp_path, monkeypatch)
        generate_claude_config(project_dir)
        content = (project_dir / "CLAUDE.md").read_text()
        assert "prompts/system.md" in content
        assert "prompts/daily-check.md" in content

    def test_generates_skills(self, tmp_path, monkeypatch):
        project_dir = _setup_project(tmp_path, monkeypatch)
        created = generate_claude_config(project_dir)
        # Skills are read from scaffold/skills/
        assert ".claude/skills/daily-check.md" in created
        assert ".claude/skills/sync-jira.md" in created
        assert ".claude/skills/sync-slack.md" in created

        daily_skill = (
            project_dir / ".claude" / "skills" / "daily-check.md"
        ).read_text()
        assert "Daily" in daily_skill

    def test_claude_cli(self, tmp_path, monkeypatch):
        _setup_project(tmp_path, monkeypatch)
        runner = CliRunner()
        result = runner.invoke(main, ["adapter", "claude"])
        assert result.exit_code == 0
        assert "Claude Code configuration generated" in result.output


class TestKiroAdapter:
    def test_generates_steering_files(self, tmp_path, monkeypatch):
        project_dir = _setup_project(tmp_path, monkeypatch)
        created = generate_kiro_config(project_dir)
        assert ".kiro/steering/product.md" in created
        assert ".kiro/steering/tech.md" in created

    def test_generates_skills(self, tmp_path, monkeypatch):
        project_dir = _setup_project(tmp_path, monkeypatch)
        created = generate_kiro_config(project_dir)
        assert ".kiro/skills/daily-check/SKILL.md" in created
        assert ".kiro/skills/sync-jira/SKILL.md" in created
        assert (project_dir / ".kiro" / "skills" / "daily-check" / "SKILL.md").is_file()

    def test_product_md_includes_project_name(self, tmp_path, monkeypatch):
        project_dir = _setup_project(tmp_path, monkeypatch)
        generate_kiro_config(project_dir)
        content = (project_dir / ".kiro" / "steering" / "product.md").read_text()
        assert "billing" in content
        assert "prompts/system.md" in content

    def test_tech_md_includes_contributing_ref(self, tmp_path, monkeypatch):
        project_dir = _setup_project(tmp_path, monkeypatch)
        generate_kiro_config(project_dir)
        content = (project_dir / ".kiro" / "steering" / "tech.md").read_text()
        assert "CONTRIBUTING.md" in content

    def test_kiro_cli(self, tmp_path, monkeypatch):
        _setup_project(tmp_path, monkeypatch)
        runner = CliRunner()
        result = runner.invoke(main, ["adapter", "kiro"])
        assert result.exit_code == 0
        assert "Kiro configuration generated" in result.output


class TestAdapterCLI:
    def test_adapter_help(self):
        runner = CliRunner()
        result = runner.invoke(main, ["adapter", "--help"])
        assert result.exit_code == 0
        assert "claude" in result.output
        assert "kiro" in result.output

    def test_adapter_no_project(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        runner = CliRunner()
        result = runner.invoke(main, ["adapter", "claude"])
        assert result.exit_code != 0
