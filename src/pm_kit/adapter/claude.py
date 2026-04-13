"""Generate Claude Code configuration files for a project."""

from pathlib import Path
from typing import Any

import yaml


def generate_claude_config(project_dir: Path) -> list[str]:
    """Generate CLAUDE.md and .claude/skills/ in the project directory.

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

    # CLAUDE.md
    claude_md = _build_claude_md(project_dir, config, project_name, run_prefix)
    (project_dir / "CLAUDE.md").write_text(claude_md)
    created.append("CLAUDE.md")

    # Deploy scaffold/skills/*.md -> .claude/skills/
    skills_src = Path(pm_kit_path) / "scaffold" / "skills" if pm_kit_path else project_dir / "skills"
    if skills_src.exists():
        dest_dir = project_dir / ".claude" / "skills"
        dest_dir.mkdir(parents=True, exist_ok=True)
        for md in sorted(skills_src.glob("*.md")):
            (dest_dir / md.name).write_text(md.read_text())
            created.append(f".claude/skills/{md.name}")

    return created


def _build_claude_md(
    project_dir: Path, _config: dict[str, Any], project_name: str, run_prefix: str
) -> str:
    lines = [
        f"# {project_name}",
        "",
        "This project is managed by pm-kit.",
        "",
        "## On Startup",
        "",
        "When starting a new conversation, read the following files:",
        "",
        "1. `policy.md` — Project-specific management rules (ticket workflow, risk process, sprint cadence, etc.)",
        "2. `data/INDEX.md` (if it exists) — Central map of all synced data sources",
        "",
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
        "## Development Policy",
        "",
        "See CONTRIBUTING.md.",
        "",
    ]

    prompts_dir = project_dir / "prompts"
    if prompts_dir.exists():
        lines.append("## Prompts")
        lines.append("")
        for p in sorted(prompts_dir.glob("*.md")):
            lines.append(f"- `prompts/{p.name}`")
        lines.append("")

    return "\n".join(lines)
