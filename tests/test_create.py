import yaml
from click.testing import CliRunner

from pm_kit.cli import main


def test_create_generates_directory_structure(tmp_path, monkeypatch):
    registry_dir = tmp_path / "xdg_data"
    monkeypatch.setenv("XDG_DATA_HOME", str(registry_dir))

    project_dir = tmp_path / "my-project"
    runner = CliRunner()
    result = runner.invoke(main, ["create", "my-project", "--path", str(project_dir)])

    assert result.exit_code == 0, result.output

    # Rendered template files
    assert (project_dir / "project.yaml").is_file()
    assert (project_dir / "policy.md").is_file()
    assert (project_dir / ".envrc").is_file()
    assert (project_dir / ".gitignore").is_file()
    assert (project_dir / "risks" / "risk-register.md").is_file()

    # Copied prompts
    assert (project_dir / "prompts" / "system.md").is_file()
    assert (project_dir / "prompts" / "risk-review.md").is_file()

    # Empty directories with .gitkeep
    assert (project_dir / "data" / "jira" / ".gitkeep").is_file()
    assert (project_dir / "data" / "slack" / ".gitkeep").is_file()
    assert (project_dir / "data" / "confluence" / ".gitkeep").is_file()
    assert (project_dir / "data" / "meetings" / ".gitkeep").is_file()
    assert (project_dir / "decisions" / ".gitkeep").is_file()

    # Symlinks
    assert (project_dir / "knowledge").is_symlink()
    # scripts symlink should no longer exist
    assert not (project_dir / "scripts").exists()


def test_create_renders_project_yaml_with_name(tmp_path, monkeypatch):
    monkeypatch.setenv("XDG_DATA_HOME", str(tmp_path / "xdg_data"))

    project_dir = tmp_path / "billing"
    runner = CliRunner()
    result = runner.invoke(main, ["create", "billing", "--path", str(project_dir)])
    assert result.exit_code == 0, result.output

    content = (project_dir / "project.yaml").read_text()
    assert 'name: "billing"' in content


def test_create_renders_policy_with_name(tmp_path, monkeypatch):
    monkeypatch.setenv("XDG_DATA_HOME", str(tmp_path / "xdg_data"))

    project_dir = tmp_path / "billing"
    runner = CliRunner()
    result = runner.invoke(main, ["create", "billing", "--path", str(project_dir)])
    assert result.exit_code == 0, result.output

    content = (project_dir / "policy.md").read_text()
    assert "billing" in content


def test_create_symlinks_point_to_pm_kit_repo(tmp_path, monkeypatch):
    monkeypatch.setenv("XDG_DATA_HOME", str(tmp_path / "xdg_data"))

    project_dir = tmp_path / "my-project"
    runner = CliRunner()
    runner.invoke(main, ["create", "my-project", "--path", str(project_dir)])

    knowledge_target = (project_dir / "knowledge").resolve()
    assert knowledge_target.name == "knowledge"
    assert (knowledge_target / "risk-management.md").is_file()


def test_create_registers_in_registry(tmp_path, monkeypatch):
    registry_dir = tmp_path / "xdg_data"
    monkeypatch.setenv("XDG_DATA_HOME", str(registry_dir))

    project_dir = tmp_path / "my-project"
    runner = CliRunner()
    runner.invoke(main, ["create", "my-project", "--path", str(project_dir)])

    registry_path = registry_dir / "pm-kit" / "registry.yaml"
    assert registry_path.is_file()

    data = yaml.safe_load(registry_path.read_text())
    assert len(data["projects"]) == 1
    assert data["projects"][0]["name"] == "my-project"
    assert data["projects"][0]["path"] == str(project_dir.resolve())


def test_create_multiple_projects_appends_to_registry(tmp_path, monkeypatch):
    registry_dir = tmp_path / "xdg_data"
    monkeypatch.setenv("XDG_DATA_HOME", str(registry_dir))

    runner = CliRunner()
    runner.invoke(main, ["create", "proj-a", "--path", str(tmp_path / "proj-a")])
    runner.invoke(main, ["create", "proj-b", "--path", str(tmp_path / "proj-b")])

    registry_path = registry_dir / "pm-kit" / "registry.yaml"
    data = yaml.safe_load(registry_path.read_text())
    assert len(data["projects"]) == 2
    names = [p["name"] for p in data["projects"]]
    assert names == ["proj-a", "proj-b"]


def test_create_fails_if_directory_exists(tmp_path, monkeypatch):
    monkeypatch.setenv("XDG_DATA_HOME", str(tmp_path / "xdg_data"))

    project_dir = tmp_path / "existing"
    project_dir.mkdir()

    runner = CliRunner()
    result = runner.invoke(main, ["create", "existing", "--path", str(project_dir)])
    assert result.exit_code != 0
    assert "already exists" in result.output


def test_create_defaults_to_cwd_name(tmp_path, monkeypatch):
    monkeypatch.setenv("XDG_DATA_HOME", str(tmp_path / "xdg_data"))
    monkeypatch.chdir(tmp_path)

    runner = CliRunner()
    result = runner.invoke(main, ["create", "default-proj"])
    assert result.exit_code == 0, result.output
    assert (tmp_path / "default-proj" / "project.yaml").is_file()
