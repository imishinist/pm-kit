"""Overview: cross-project summary and risk aggregation."""

from pathlib import Path

import click
import yaml

from pm_kit.create import get_registry_path


def _load_registry() -> list[dict]:
    registry_path = get_registry_path()
    if not registry_path.exists():
        return []
    data = yaml.safe_load(registry_path.read_text()) or {}
    return data.get("projects", [])


def _read_risk_register(project_dir: Path) -> str | None:
    risk_file = project_dir / "risks" / "risk-register.md"
    if risk_file.exists():
        return risk_file.read_text()
    return None


def _read_board_summary(project_dir: Path) -> str | None:
    board_file = project_dir / "data" / "jira" / "board.md"
    if board_file.exists():
        return board_file.read_text()
    return None


def build_overview() -> str:
    """Build a cross-project overview."""
    projects = _load_registry()
    if not projects:
        return "No projects registered. Use `pm-kit create` to create a project.\n"

    sections: list[str] = []
    sections.append("# pm-kit Overview")
    sections.append("")
    sections.append(f"Total projects: {len(projects)}")
    sections.append("")

    # Project list
    sections.append("## Projects")
    sections.append("")
    for proj in projects:
        name = proj.get("name", "unknown")
        path = proj.get("path", "")
        created = proj.get("created", "")
        project_dir = Path(path)

        status = "ok" if project_dir.exists() else "missing"
        sections.append(f"### {name}")
        sections.append(f"- Path: `{path}`")
        sections.append(f"- Created: {created}")
        sections.append(f"- Status: {status}")

        if project_dir.exists():
            config_path = project_dir / "project.yaml"
            if config_path.exists():
                config = yaml.safe_load(config_path.read_text()) or {}
                desc = config.get("description", "")
                if desc:
                    sections.append(f"- Description: {desc}")

            board = _read_board_summary(project_dir)
            if board:
                sections.append(f"- Board: synced")

        sections.append("")

    # Risk aggregation
    sections.append("## Risks (All Projects)")
    sections.append("")
    has_risks = False
    for proj in projects:
        project_dir = Path(proj.get("path", ""))
        if not project_dir.exists():
            continue
        risks = _read_risk_register(project_dir)
        if risks and risks.strip():
            has_risks = True
            sections.append(f"### {proj.get('name', 'unknown')}")
            sections.append(risks)
            sections.append("")

    if not has_risks:
        sections.append("No risks registered across projects.")
        sections.append("")

    return "\n".join(sections)


@click.command()
def overview():
    """Show cross-project overview and aggregated risks."""
    output = build_overview()
    click.echo(output)
