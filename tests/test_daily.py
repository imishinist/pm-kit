import json
from pathlib import Path

from click.testing import CliRunner

from pm_kit.cli import main
from pm_kit.daily import gather_daily_context


def _setup_project(tmp_path, monkeypatch):
    """Create a minimal project directory and chdir into it."""
    (tmp_path / "project.yaml").write_text('name: "test-project"\n')
    (tmp_path / "prompts").mkdir()
    (tmp_path / "prompts" / "daily-check.md").write_text("# Daily Check Prompt\n")
    (tmp_path / "risks").mkdir()
    (tmp_path / "data" / "jira" / "tickets").mkdir(parents=True)
    (tmp_path / "data" / "jira" / "sprints").mkdir(parents=True)
    (tmp_path / "data" / "slack" / "digest").mkdir(parents=True)
    (tmp_path / "data" / "slack" / "raw").mkdir(parents=True)
    (tmp_path / "data" / "confluence").mkdir(parents=True)
    monkeypatch.chdir(tmp_path)
    return tmp_path


class TestGatherDailyContext:
    def test_minimal_project(self, tmp_path, monkeypatch):
        project_dir = _setup_project(tmp_path, monkeypatch)
        context = gather_daily_context(project_dir)
        assert "Daily Check" in context
        assert "test-project" in context

    def test_includes_board_summary(self, tmp_path, monkeypatch):
        project_dir = _setup_project(tmp_path, monkeypatch)
        (project_dir / "data" / "jira" / "board.md").write_text("# Board\nTotal: 10\n")
        context = gather_daily_context(project_dir)
        assert "Board Summary" in context
        assert "Total: 10" in context

    def test_includes_sprint_current(self, tmp_path, monkeypatch):
        project_dir = _setup_project(tmp_path, monkeypatch)
        (project_dir / "data" / "jira" / "sprints" / "current.md").write_text(
            "---\nname: Sprint 5\n---\n"
        )
        context = gather_daily_context(project_dir)
        assert "Current Sprint" in context
        assert "Sprint 5" in context

    def test_includes_active_tickets(self, tmp_path, monkeypatch):
        project_dir = _setup_project(tmp_path, monkeypatch)
        ticket_dir = project_dir / "data" / "jira" / "tickets" / "TEST-1"
        ticket_dir.mkdir()
        (ticket_dir / "ticket.md").write_text(
            '---\nkey: "TEST-1"\nsummary: "Fix bug"\n---\n\n# TEST-1: Fix bug\n\nDetails\n'
        )
        context = gather_daily_context(project_dir)
        assert "Active Tickets" in context
        assert "TEST-1" in context

    def test_excludes_frontmatter_only_tickets(self, tmp_path, monkeypatch):
        project_dir = _setup_project(tmp_path, monkeypatch)
        ticket_dir = project_dir / "data" / "jira" / "tickets" / "TEST-2"
        ticket_dir.mkdir()
        (ticket_dir / "ticket.md").write_text(
            '---\nkey: "TEST-2"\nsummary: "Old ticket"\n---\n'
        )
        context = gather_daily_context(project_dir)
        assert "Active Tickets" not in context

    def test_includes_risk_register(self, tmp_path, monkeypatch):
        project_dir = _setup_project(tmp_path, monkeypatch)
        (project_dir / "risks" / "risk-register.md").write_text(
            "# Risks\n| ID | Title |\n|----|-------|\n| R1 | Delay |\n"
        )
        context = gather_daily_context(project_dir)
        assert "Risk Register" in context
        assert "Delay" in context

    def test_includes_slack_raw_when_no_digest(self, tmp_path, monkeypatch):
        from datetime import date

        project_dir = _setup_project(tmp_path, monkeypatch)
        channel_dir = project_dir / "data" / "slack" / "raw" / "general"
        channel_dir.mkdir(parents=True)
        today = str(date.today())
        record = {"ts": "100", "user": "U01", "text": "hello", "replies": []}
        (channel_dir / f"{today}.jsonl").write_text(json.dumps(record) + "\n")

        context = gather_daily_context(project_dir)
        assert "Slack Messages" in context
        assert "hello" in context

    def test_includes_daily_check_prompt(self, tmp_path, monkeypatch):
        project_dir = _setup_project(tmp_path, monkeypatch)
        context = gather_daily_context(project_dir)
        assert "Daily Check Prompt" in context


class TestDailyCLI:
    def test_daily_help(self):
        runner = CliRunner()
        result = runner.invoke(main, ["daily", "--help"])
        assert result.exit_code == 0
        assert "daily check" in result.output.lower()

    def test_daily_in_project(self, tmp_path, monkeypatch):
        _setup_project(tmp_path, monkeypatch)
        runner = CliRunner()
        result = runner.invoke(main, ["daily"])
        assert result.exit_code == 0
        assert "test-project" in result.output

    def test_daily_no_project(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        runner = CliRunner()
        result = runner.invoke(main, ["daily"])
        assert result.exit_code != 0
