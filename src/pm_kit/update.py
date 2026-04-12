import difflib
import shutil
from pathlib import Path

import click

from pm_kit.create import get_pm_kit_root
from pm_kit.project import load_project


def _update_directory(
    scaffold_src: Path, project_dst: Path, label: str
) -> tuple[int, int, int]:
    """Update a directory from scaffold source. Returns (added, updated, skipped) counts."""
    if not project_dst.exists():
        click.echo(f"{label}/ directory not found. Copying from scaffold...")
        shutil.copytree(scaffold_src, project_dst)
        count = sum(1 for f in scaffold_src.iterdir() if f.is_file())
        return (count, 0, 0)

    updated = 0
    skipped = 0
    added = 0

    for src_file in sorted(scaffold_src.iterdir()):
        if not src_file.is_file():
            continue

        dst_file = project_dst / src_file.name
        src_content = src_file.read_text()

        if not dst_file.exists():
            dst_file.write_text(src_content)
            click.echo(f"  added: {label}/{src_file.name}")
            added += 1
            continue

        dst_content = dst_file.read_text()

        if src_content == dst_content:
            updated += 1
            continue

        click.echo(f"\n{label}/{src_file.name} has local changes:")
        diff = difflib.unified_diff(
            dst_content.splitlines(keepends=True),
            src_content.splitlines(keepends=True),
            fromfile=f"project/{src_file.name}",
            tofile=f"scaffold/{src_file.name}",
        )
        click.echo("".join(diff))

        if click.confirm("  Overwrite with scaffold version?", default=False):
            dst_file.write_text(src_content)
            click.echo(f"  updated: {label}/{src_file.name}")
            updated += 1
        else:
            click.echo(f"  skipped: {label}/{src_file.name}")
            skipped += 1

    return (added, updated, skipped)


def _update_kiro_skills(
    scaffold_skills: Path, project_path: Path
) -> tuple[int, int, int]:
    """Update .kiro/skills/<name>/SKILL.md from scaffold/skills/*.md."""
    added = 0
    updated = 0
    skipped = 0

    for src_file in sorted(scaffold_skills.glob("*.md")):
        name = src_file.stem
        dst_file = project_path / ".kiro" / "skills" / name / "SKILL.md"
        src_content = src_file.read_text()
        label = f".kiro/skills/{name}/SKILL.md"

        if not dst_file.exists():
            dst_file.parent.mkdir(parents=True, exist_ok=True)
            dst_file.write_text(src_content)
            click.echo(f"  added: {label}")
            added += 1
            continue

        dst_content = dst_file.read_text()

        if src_content == dst_content:
            updated += 1
            continue

        click.echo(f"\n{label} has local changes:")
        diff = difflib.unified_diff(
            dst_content.splitlines(keepends=True),
            src_content.splitlines(keepends=True),
            fromfile=f"project/{name}/SKILL.md",
            tofile=f"scaffold/{src_file.name}",
        )
        click.echo("".join(diff))

        if click.confirm("  Overwrite with scaffold version?", default=False):
            dst_file.write_text(src_content)
            click.echo(f"  updated: {label}")
            updated += 1
        else:
            click.echo(f"  skipped: {label}")
            skipped += 1

    return (added, updated, skipped)


def _update_claude_skills(
    scaffold_skills: Path, project_path: Path
) -> tuple[int, int, int]:
    """Update .claude/skills/*.md from scaffold/skills/*.md."""
    dest_dir = project_path / ".claude" / "skills"
    if not dest_dir.exists():
        return (0, 0, 0)
    return _update_directory(scaffold_skills, dest_dir, ".claude/skills")


@click.command()
@click.argument("project_dir", type=click.Path(exists=True, file_okay=False))
def update(project_dir: str) -> None:
    """Update project prompts and skills from the latest pm-kit scaffold."""
    project_path = Path(project_dir)
    config = load_project(project_path)
    pm_kit_path = config.get("pm_kit_path", "")
    pm_kit_root = Path(pm_kit_path) if pm_kit_path else get_pm_kit_root()
    scaffold_skills = pm_kit_root / "scaffold" / "skills"

    total_added = 0
    total_updated = 0
    total_skipped = 0

    # Update prompts/
    scaffold_prompts = pm_kit_root / "scaffold" / "prompts"
    if scaffold_prompts.exists():
        a, u, s = _update_directory(scaffold_prompts, project_path / "prompts", "prompts")
        total_added += a
        total_updated += u
        total_skipped += s

    # Update .kiro/skills/
    if (project_path / ".kiro" / "skills").exists() and scaffold_skills.exists():
        a, u, s = _update_kiro_skills(scaffold_skills, project_path)
        total_added += a
        total_updated += u
        total_skipped += s

    # Update .claude/skills/
    if (project_path / ".claude" / "skills").exists() and scaffold_skills.exists():
        a, u, s = _update_claude_skills(scaffold_skills, project_path)
        total_added += a
        total_updated += u
        total_skipped += s

    click.echo(
        f"\nUpdate complete: {total_added} added, {total_updated} up-to-date, {total_skipped} skipped"
    )
