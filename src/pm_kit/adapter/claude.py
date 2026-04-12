"""Generate Claude Code configuration files for a project."""

from pathlib import Path

import yaml


def generate_claude_config(project_dir: Path) -> list[str]:
    """Generate CLAUDE.md and .claude/skills/ in the project directory.

    Returns a list of file paths that were created/updated.
    """
    config_path = project_dir / "project.yaml"
    config = yaml.safe_load(config_path.read_text()) if config_path.exists() else {}
    project_name = config.get("name", "project")

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


def _build_claude_md(project_dir: Path, config: dict, project_name: str) -> str:
    lines = [
        f"# {project_name}",
        "",
        "このプロジェクトは pm-kit で管理されています。",
        "",
        "## 参照すべきファイル",
        "",
        "- `project.yaml` — プロジェクト設定",
        "- `policy.md` — プロジェクトポリシー",
        "- `prompts/` — AI への指示プロンプト集",
        "- `knowledge/` — PM 知識ベース",
        "- `data/` — 外部サービスから同期されたデータ",
        "- `risks/` — リスク一覧",
        "- `decisions/` — 意思決定ログ",
        "",
        "## 利用可能なコマンド",
        "",
        "```bash",
        "pm-kit daily              # デイリーチェック",
        "pm-kit sync jira          # Jira 同期",
        "pm-kit sync slack         # Slack 同期",
        "pm-kit sync confluence    # Confluence 同期",
        "```",
        "",
        "## 開発ポリシー",
        "",
        "CONTRIBUTING.md を参照。",
        "",
    ]

    # Add prompt index
    prompts_dir = project_dir / "prompts"
    if prompts_dir.exists():
        lines.append("## プロンプト一覧")
        lines.append("")
        for p in sorted(prompts_dir.glob("*.md")):
            lines.append(f"- `prompts/{p.name}`")
        lines.append("")

    return "\n".join(lines)


def _build_skills(config: dict) -> dict[str, str]:
    skills = {}

    skills["daily-check.md"] = "\n".join([
        "---",
        "name: daily-check",
        "description: デイリーチェックを実行し、プロジェクト状況を分析する",
        "---",
        "",
        "1. `pm-kit sync jira` でJiraを同期（設定済みの場合）",
        "2. `pm-kit sync slack` でSlackを同期（設定済みの場合）",
        "3. `pm-kit daily` を実行して分析コンテキストを取得",
        "4. 出力内容を元に `prompts/daily-check.md` の指示に従って分析・報告",
        "",
    ])

    skills["sync-all.md"] = "\n".join([
        "---",
        "name: sync-all",
        "description: 全データソースを一括同期する",
        "---",
        "",
        "以下を順に実行:",
        "",
        "1. `pm-kit sync jira`（jira が設定されている場合）",
        "2. `pm-kit sync slack`（slack が設定されている場合）",
        "3. `pm-kit sync confluence`（confluence が設定されている場合）",
        "",
    ])

    skills["risk-review.md"] = "\n".join([
        "---",
        "name: risk-review",
        "description: リスクレビューを実行する",
        "---",
        "",
        "1. `risks/risk-register.md` を読み込む",
        "2. `prompts/risk-review.md` の指示に従ってリスクを分析",
        "3. 同期データから新たなリスク兆候を検出",
        "4. risk-register.md の更新を提案",
        "",
    ])

    return skills
