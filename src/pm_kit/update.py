import difflib
import shutil
from pathlib import Path

import click

from pm_kit.create import get_pm_kit_root


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


@click.command()
@click.argument("project_dir", type=click.Path(exists=True, file_okay=False))
def update(project_dir: str) -> None:
    """Update project prompts and skills from the latest pm-kit scaffold."""
    project_path = Path(project_dir)
    pm_kit_root = get_pm_kit_root()

    total_added = 0
    total_updated = 0
    total_skipped = 0

    for label in ["prompts", "skills"]:
        scaffold_src = pm_kit_root / "scaffold" / label
        if not scaffold_src.exists():
            continue
        project_dst = project_path / label
        added, updated, skipped = _update_directory(scaffold_src, project_dst, label)
        total_added += added
        total_updated += updated
        total_skipped += skipped

    click.echo(
        f"\nUpdate complete: {total_added} added, {total_updated} up-to-date, {total_skipped} skipped"
    )
