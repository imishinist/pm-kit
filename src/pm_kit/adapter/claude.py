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

    created: list[str] = []

    # CLAUDE.md
    claude_md = _build_claude_md(project_dir, config, project_name)
    (project_dir / "CLAUDE.md").write_text(claude_md)
    created.append("CLAUDE.md")

    # .claude/skills/
    skills_dir = project_dir / ".claude" / "skills"
    skills_dir.mkdir(parents=True, exist_ok=True)

    skills = _build_skills(config)
    for filename, content in skills.items():
        (skills_dir / filename).write_text(content)
        created.append(f".claude/skills/{filename}")

    return created


def _build_claude_md(
    project_dir: Path, _config: dict[str, Any], project_name: str
) -> str:
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
        "## Development Policy",
        "",
        "See CONTRIBUTING.md.",
        "",
    ]

    # Add prompt index
    prompts_dir = project_dir / "prompts"
    if prompts_dir.exists():
        lines.append("## Prompts")
        lines.append("")
        for p in sorted(prompts_dir.glob("*.md")):
            lines.append(f"- `prompts/{p.name}`")
        lines.append("")

    return "\n".join(lines)


def _build_skills(_config: dict[str, Any]) -> dict[str, str]:
    skills: dict[str, str] = {}

    skills["daily-check.md"] = "\n".join(
        [
            "---",
            "name: daily-check",
            "description: Run daily check and analyze project status",
            "---",
            "",
            "1. Run `pm-kit sync jira` to sync Jira (if configured)",
            "2. Run `pm-kit sync slack` to sync Slack (if configured)",
            "3. Run `pm-kit daily` to gather analysis context",
            "4. Analyze and report based on the output, following `prompts/daily-check.md`",
            "",
        ]
    )

    skills["sync-all.md"] = "\n".join(
        [
            "---",
            "name: sync-all",
            "description: Sync all configured data sources",
            "---",
            "",
            "Run the following in order:",
            "",
            "1. `pm-kit sync jira` (if jira is configured)",
            "2. `pm-kit sync slack` (if slack is configured)",
            "3. `pm-kit sync confluence` (if confluence is configured)",
            "",
        ]
    )

    skills["risk-review.md"] = "\n".join(
        [
            "---",
            "name: risk-review",
            "description: Run a risk review",
            "---",
            "",
            "1. Read `risks/risk-register.md`",
            "2. Analyze risks following `prompts/risk-review.md`",
            "3. Detect new risk indicators from synced data",
            "4. Propose updates to risk-register.md",
            "",
        ]
    )

    return skills
