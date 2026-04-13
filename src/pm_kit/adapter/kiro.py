"""Generate Kiro configuration files for a project."""

from pathlib import Path
from typing import Any

import yaml


def generate_kiro_config(project_dir: Path) -> list[str]:
    """Generate .kiro/steering/ and .kiro/skills/ files in the project directory.

    Returns a list of file paths that were created/updated.
    """
    config_path = project_dir / "project.yaml"
    config: dict[str, Any] = (
        yaml.safe_load(config_path.read_text()) if config_path.exists() else {}
    )
    project_name: str = config.get("name", "project")
    pm_kit_path: str = config.get("pm_kit_path", "")
    run_prefix = f"uv run --project {pm_kit_path} pm-kit" if pm_kit_path else "pm-kit"

    created: list[str] = []

    steering_dir = project_dir / ".kiro" / "steering"
    steering_dir.mkdir(parents=True, exist_ok=True)

    files = _build_steering_files(project_dir, config, project_name, run_prefix)
    for filename, content in files.items():
        (steering_dir / filename).write_text(content)
        created.append(f".kiro/steering/{filename}")

    # Deploy scaffold/skills/*.md -> .kiro/skills/<name>/SKILL.md
    skills_src = Path(pm_kit_path) / "scaffold" / "skills" if pm_kit_path else project_dir / "skills"
    if skills_src.exists():
        for md in sorted(skills_src.glob("*.md")):
            name = md.stem
            dest_dir = project_dir / ".kiro" / "skills" / name
            dest_dir.mkdir(parents=True, exist_ok=True)
            (dest_dir / "SKILL.md").write_text(md.read_text())
            created.append(f".kiro/skills/{name}/SKILL.md")

    return created


def _build_steering_files(
    project_dir: Path, _config: dict[str, Any], project_name: str, run_prefix: str
) -> dict[str, str]:
    files: dict[str, str] = {}

    lines = [
        f"# {project_name}",
        "",
        "This project is managed by pm-kit.",
        "",
        "## On Startup",
        "",
        "When starting a new conversation, first read `data/INDEX.md` if it exists.",
        "This file summarizes all synced data sources and where to find specific information.",
        "If `data/INDEX.md` does not exist and `data/` contains files, run the **build-index** skill to generate it.",
        "",
        "## Files to Reference",
        "",
        "- `project.yaml` — Project configuration",
        "- `policy.md` — Project policy",
        "- `prompts/` — AI instruction prompts",
        "- `knowledge/` — PM knowledge base",
        "- `data/INDEX.md` — Central map of all synced data (read this first)",
        "- `data/` — Data synced from external services",
        "- `risks/` — Risk register",
        "- `decisions/` — Decision log",
        "",
        "## Available Commands",
        "",
        "```bash",
        f"{run_prefix} daily              # Daily check",
        f"{run_prefix} sync jira          # Sync Jira",
        f"{run_prefix} sync slack         # Sync Slack",
        f"{run_prefix} sync confluence    # Sync Confluence",
        "```",
        "",
    ]

    prompts_dir = project_dir / "prompts"
    if prompts_dir.exists():
        lines.append("## Prompts")
        lines.append("")
        for p in sorted(prompts_dir.glob("*.md")):
            lines.append(f"- `prompts/{p.name}`")
        lines.append("")

    files["product.md"] = "\n".join(lines)

    files["tech.md"] = "\n".join(
        [
            "# Tech Stack",
            "",
            "- pm-kit: Python (uv), Click CLI",
            "- Data formats: YAML, Markdown, JSONL",
            "- External integrations: Jira REST API, Slack Web API, Confluence REST API",
            "",
            "## Development Policy",
            "",
            "See CONTRIBUTING.md.",
            "",
        ]
    )

    return files
