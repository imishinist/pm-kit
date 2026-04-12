import click

from pm_kit.adapter.claude import generate_claude_config
from pm_kit.adapter.kiro import generate_kiro_config
from pm_kit.project import find_project_dir


@click.group()
def adapter():
    """Generate AI tool configuration files."""
    pass


@adapter.command()
def claude():
    """Generate Claude Code configuration (CLAUDE.md, .claude/skills/)."""
    project_dir = find_project_dir()
    created = generate_claude_config(project_dir)
    for f in created:
        click.echo(f"  created: {f}")
    click.echo("Claude Code configuration generated.")


@adapter.command()
def kiro():
    """Generate Kiro configuration (.kiro/steering/)."""
    project_dir = find_project_dir()
    created = generate_kiro_config(project_dir)
    for f in created:
        click.echo(f"  created: {f}")
    click.echo("Kiro configuration generated.")
