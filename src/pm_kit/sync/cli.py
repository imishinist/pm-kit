import click

from pm_kit.project import find_project_dir, load_project
from pm_kit.sync.confluence import sync_confluence
from pm_kit.sync.jira import sync_jira
from pm_kit.sync.slack import sync_slack


@click.group()
def sync():
    """Sync external data sources into the project."""
    pass


@sync.command()
def jira():
    """Sync Jira tickets and sprints."""
    project_dir = find_project_dir()
    config = load_project(project_dir)
    sync_jira(project_dir, config)


@sync.command()
def slack():
    """Sync Slack channel messages."""
    project_dir = find_project_dir()
    config = load_project(project_dir)
    sync_slack(project_dir, config)


@sync.command()
def confluence():
    """Sync Confluence pages."""
    project_dir = find_project_dir()
    config = load_project(project_dir)
    sync_confluence(project_dir, config)
