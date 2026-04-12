from pathlib import Path

import yaml
from click.testing import CliRunner

from pm_kit.cli import main
from pm_kit.overview import build_overview


def _write_registry(registry_path, projects):
    registry_path.parent.mkdir(parents=True, exist_ok=True)
    registry_path.write_text(yaml.dump({"projects": projects}, allow_unicode=True))


class TestBuildOverview:
    def test_no_projects(self, tmp_path, monkeypatch):
        monkeypatch.setenv("XDG_DATA_HOME", str(tmp_path / "xdg"))
        output = build_overview()
        assert "No projects registered" in output

    def test_single_project(self, tmp_path, monkeypatch):
        xdg = tmp_path / "xdg"
        monkeypatch.setenv("XDG_DATA_HOME", str(xdg))

        project_dir = tmp_path / "my-project"
        project_dir.mkdir()
        (project_dir / "project.yaml").write_text('name: "my-project"\ndescription: "Test"\n')

        _write_registry(
            xdg / "pm-kit" / "registry.yaml",
            [{"name": "my-project", "path": str(project_dir), "created": "2026-04-12"}],
        )

        output = build_overview()
        assert "my-project" in output
        assert "2026-04-12" in output
        assert "Test" in output

    def test_missing_project_dir(self, tmp_path, monkeypatch):
        xdg = tmp_path / "xdg"
        monkeypatch.setenv("XDG_DATA_HOME", str(xdg))

        _write_registry(
            xdg / "pm-kit" / "registry.yaml",
            [{"name": "gone", "path": str(tmp_path / "nonexistent"), "created": "2026-04-12"}],
        )

        output = build_overview()
        assert "missing" in output

    def test_risk_aggregation(self, tmp_path, monkeypatch):
        xdg = tmp_path / "xdg"
        monkeypatch.setenv("XDG_DATA_HOME", str(xdg))

        proj_a = tmp_path / "proj-a"
        proj_a.mkdir()
        (proj_a / "project.yaml").write_text('name: "proj-a"\n')
        (proj_a / "risks").mkdir()
        (proj_a / "risks" / "risk-register.md").write_text(
            "| R1 | Auth delay | high |\n"
        )

        proj_b = tmp_path / "proj-b"
        proj_b.mkdir()
        (proj_b / "project.yaml").write_text('name: "proj-b"\n')
        (proj_b / "risks").mkdir()
        (proj_b / "risks" / "risk-register.md").write_text(
            "| R1 | Vendor risk | medium |\n"
        )

        _write_registry(
            xdg / "pm-kit" / "registry.yaml",
            [
                {"name": "proj-a", "path": str(proj_a), "created": "2026-04-12"},
                {"name": "proj-b", "path": str(proj_b), "created": "2026-04-13"},
            ],
        )

        output = build_overview()
        assert "Risks (All Projects)" in output
        assert "Auth delay" in output
        assert "Vendor risk" in output

    def test_no_risks(self, tmp_path, monkeypatch):
        xdg = tmp_path / "xdg"
        monkeypatch.setenv("XDG_DATA_HOME", str(xdg))

        proj = tmp_path / "proj"
        proj.mkdir()
        (proj / "project.yaml").write_text('name: "proj"\n')

        _write_registry(
            xdg / "pm-kit" / "registry.yaml",
            [{"name": "proj", "path": str(proj), "created": "2026-04-12"}],
        )

        output = build_overview()
        assert "No risks registered" in output


class TestOverviewCLI:
    def test_overview_help(self):
        runner = CliRunner()
        result = runner.invoke(main, ["overview", "--help"])
        assert result.exit_code == 0

    def test_overview_empty(self, tmp_path, monkeypatch):
        monkeypatch.setenv("XDG_DATA_HOME", str(tmp_path / "xdg"))
        runner = CliRunner()
        result = runner.invoke(main, ["overview"])
        assert result.exit_code == 0
        assert "No projects registered" in result.output
