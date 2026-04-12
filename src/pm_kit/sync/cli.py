import click

from pm_kit.project import find_project_dir, load_project
from pm_kit.sync.confluence import sync_confluence as run_sync_confluence
from pm_kit.sync.jira import sync_jira as run_sync_jira
from pm_kit.sync.slack import sync_slack as run_sync_slack


@click.group()
def sync() -> None:
    """Sync external data sources into the project."""
    pass


@sync.command()
def jira() -> None:
    """Sync Jira tickets and sprints."""
    project_dir = find_project_dir()
    config = load_project(project_dir)
    run_sync_jira(project_dir, config)


@sync.command()
def slack() -> None:
    """Sync Slack channel messages."""
    project_dir = find_project_dir()
    config = load_project(project_dir)
    run_sync_slack(project_dir, config)


@sync.command()
def confluence() -> None:
    """Sync Confluence pages."""
    project_dir = find_project_dir()
    config = load_project(project_dir)
    run_sync_confluence(project_dir, config)
