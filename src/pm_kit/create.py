import os
import shutil
import subprocess
from datetime import date
from pathlib import Path
from typing import Any

import click
import yaml
from jinja2 import Environment, FileSystemLoader


def get_registry_path() -> Path:
    xdg_data = os.environ.get("XDG_DATA_HOME", str(Path.home() / ".local" / "share"))
    return Path(xdg_data) / "pm-kit" / "registry.yaml"


def get_pm_kit_root() -> Path:
    return Path(__file__).resolve().parent.parent.parent


def render_template(
    template_path: Path, output_path: Path, variables: dict[str, Any]
) -> None:
    env = Environment(
        loader=FileSystemLoader(str(template_path.parent)),
        keep_trailing_newline=True,
    )
    template = env.get_template(template_path.name)
    output_path.write_text(template.render(**variables))


def register_project(name: str, project_dir: Path) -> None:
    registry_path = get_registry_path()
    registry_path.parent.mkdir(parents=True, exist_ok=True)

    data: dict[str, Any]
    if registry_path.exists():
        data = yaml.safe_load(registry_path.read_text()) or {}
    else:
        data = {}

    projects: list[dict[str, Any]] = data.get("projects", [])
    projects.append(
        {
            "name": name,
            "path": str(project_dir.resolve()),
            "created": str(date.today()),
        }
    )
    data["projects"] = projects

    registry_path.write_text(
        yaml.dump(data, default_flow_style=False, allow_unicode=True)
    )


@click.command()
@click.argument("name")
@click.option(
    "--path",
    "dest_path",
    type=click.Path(),
    default=None,
    help="Directory to create the project in (default: ./<name>)",
)
def create(name: str, dest_path: str | None) -> None:
    """Create a new project from the pm-kit scaffold."""
    project_dir = Path(dest_path) if dest_path else Path.cwd() / name

    if project_dir.exists():
        raise click.ClickException(f"Directory already exists: {project_dir}")

    pm_kit_root = get_pm_kit_root()
    scaffold_dir = pm_kit_root / "scaffold"

    variables = {
        "name": name,
        "description": "",
        "created_date": str(date.today()),
        "pm_kit_path": str(pm_kit_root),
    }

    project_dir.mkdir(parents=True)

    # Initialize git repo with empty commit
    subprocess.run(["git", "init"], cwd=project_dir, check=True, capture_output=True)
    subprocess.run(
        ["git", "commit", "--allow-empty", "-m", "initial commit"],
        cwd=project_dir,
        check=True,
        capture_output=True,
    )

    # Render .template files
    templates = {
        scaffold_dir / "project.yaml.template": project_dir / "project.yaml",
        scaffold_dir / "policy.md.template": project_dir / "policy.md",
        scaffold_dir / ".envrc.template": project_dir / ".envrc",
        scaffold_dir / ".gitignore.template": project_dir / ".gitignore",
        scaffold_dir / "risks" / "risk-register.md.template": project_dir
        / "risks"
        / "risk-register.md",
    }

    for src, dst in templates.items():
        dst.parent.mkdir(parents=True, exist_ok=True)
        render_template(src, dst, variables)

    # Copy prompts/
    shutil.copytree(scaffold_dir / "prompts", project_dir / "prompts")

    # Create empty directories
    for subdir in [
        "data/jira",
        "data/slack",
        "data/confluence",
        "data/meetings",
        "data/repos",
        "decisions",
    ]:
        d = project_dir / subdir
        d.mkdir(parents=True)
        (d / ".gitkeep").touch()

    # Symlinks
    (project_dir / "knowledge").symlink_to(pm_kit_root / "knowledge")

    # Register
    register_project(name, project_dir)

    click.echo(f"Project created: {project_dir}")
    click.echo()
    click.echo("Next steps:")
    click.echo(
        "  1. Run the create-interview prompt with your AI tool to fill in project.yaml"
    )
    click.echo("  2. Set up authentication in .envrc")
