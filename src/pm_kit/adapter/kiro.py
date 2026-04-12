"""Generate Kiro configuration files for a project."""

from pathlib import Path
from typing import Any

import yaml


def generate_kiro_config(project_dir: Path) -> list[str]:
    """Generate .kiro/steering/ files in the project directory.

    Returns a list of file paths that were created/updated.
    """
    config_path = project_dir / "project.yaml"
    config: dict[str, Any] = (
        yaml.safe_load(config_path.read_text()) if config_path.exists() else {}
    )
    project_name: str = config.get("name", "project")

    created: list[str] = []

    steering_dir = project_dir / ".kiro" / "steering"
    steering_dir.mkdir(parents=True, exist_ok=True)

    files = _build_steering_files(project_dir, config, project_name)
    for filename, content in files.items():
        (steering_dir / filename).write_text(content)
        created.append(f".kiro/steering/{filename}")

    return created


def _build_steering_files(
    project_dir: Path, _config: dict[str, Any], project_name: str
) -> dict[str, str]:
    files: dict[str, str] = {}

    # product.md — product context
    lines = [
        f"# {project_name}",
        "",
        "This project is managed by pm-kit.",
        "",
        "## Files to Reference",
        "",
        "- `project.yaml` — Project configuration",
        "- `policy.md` — Project policy",
        "- `prompts/` — AI instruction prompts",
        "- `knowledge/` — PM knowledge base",
        "- `data/` — Data synced from external services",
        "- `risks/` — Risk register",
        "- `decisions/` — Decision log",
        "",
        "## Available Commands",
        "",
        "```bash",
        "pm-kit daily              # Daily check",
        "pm-kit sync jira          # Sync Jira",
        "pm-kit sync slack         # Sync Slack",
        "pm-kit sync confluence    # Sync Confluence",
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

    # tech.md — technical context
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
