"""Generate Kiro configuration files for a project."""

from pathlib import Path

import yaml


def generate_kiro_config(project_dir: Path) -> list[str]:
    """Generate .kiro/steering/ files in the project directory.

    Returns a list of file paths that were created/updated.
    """
    config_path = project_dir / "project.yaml"
    config = yaml.safe_load(config_path.read_text()) if config_path.exists() else {}
    project_name = config.get("name", "project")

    created: list[str] = []

    steering_dir = project_dir / ".kiro" / "steering"
    steering_dir.mkdir(parents=True, exist_ok=True)

    files = _build_steering_files(project_dir, config, project_name)
    for filename, content in files.items():
        (steering_dir / filename).write_text(content)
        created.append(f".kiro/steering/{filename}")

    return created


def _build_steering_files(project_dir: Path, config: dict, project_name: str) -> dict[str, str]:
    files = {}

    # product.md — product context
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
    ]

    prompts_dir = project_dir / "prompts"
    if prompts_dir.exists():
        lines.append("## プロンプト一覧")
        lines.append("")
        for p in sorted(prompts_dir.glob("*.md")):
            lines.append(f"- `prompts/{p.name}`")
        lines.append("")

    files["product.md"] = "\n".join(lines)

    # tech.md — technical context
    files["tech.md"] = "\n".join([
        "# 技術スタック",
        "",
        "- pm-kit: Python (uv), Click CLI",
        "- データ形式: YAML, Markdown, JSONL",
        "- 外部連携: Jira REST API, Slack Web API, Confluence REST API",
        "",
        "## 開発ポリシー",
        "",
        "CONTRIBUTING.md を参照。",
        "",
    ])

    return files
