import difflib
import shutil
from pathlib import Path

import click

from pm_kit.create import get_pm_kit_root


@click.command()
@click.argument("project_dir", type=click.Path(exists=True, file_okay=False))
def update(project_dir: str) -> None:
    """Update project prompts from the latest pm-kit scaffold."""
    project_path = Path(project_dir)
    scaffold_prompts = get_pm_kit_root() / "scaffold" / "prompts"
    project_prompts = project_path / "prompts"

    if not project_prompts.exists():
        click.echo("prompts/ directory not found. Copying from scaffold...")
        shutil.copytree(scaffold_prompts, project_prompts)
        click.echo("Done.")
        return

    updated = 0
    skipped = 0
    added = 0

    for src_file in sorted(scaffold_prompts.iterdir()):
        if not src_file.is_file():
            continue

        dst_file = project_prompts / src_file.name
        src_content = src_file.read_text()

        if not dst_file.exists():
            # New file in scaffold — just copy
            dst_file.write_text(src_content)
            click.echo(f"  added: prompts/{src_file.name}")
            added += 1
            continue

        dst_content = dst_file.read_text()

        if src_content == dst_content:
            # Identical — overwrite silently (no-op)
            updated += 1
            continue

        # Content differs — show diff and ask
        click.echo(f"\nprompts/{src_file.name} has local changes:")
        diff = difflib.unified_diff(
            dst_content.splitlines(keepends=True),
            src_content.splitlines(keepends=True),
            fromfile=f"project/{src_file.name}",
            tofile=f"scaffold/{src_file.name}",
        )
        click.echo("".join(diff))

        if click.confirm("  Overwrite with scaffold version?", default=False):
            dst_file.write_text(src_content)
            click.echo(f"  updated: prompts/{src_file.name}")
            updated += 1
        else:
            click.echo(f"  skipped: prompts/{src_file.name}")
            skipped += 1

    click.echo(
        f"\nUpdate complete: {added} added, {updated} up-to-date, {skipped} skipped"
    )
