import click

from pm_kit.project import find_project_dir, load_project
from pm_kit.sync.confluence import sync_confluence as run_sync_confluence
from pm_kit.sync.jira import sync_jira as run_sync_jira
from pm_kit.sync.slack import sync_slack as run_sync_slack


@click.group()
def sync() -> None:
    """Fetch external data and output as JSON."""
    pass


@sync.command()
@click.option("--since", default=None, help="Fetch tickets updated since this date (YYYY-MM-DD). Omit for all tickets.")
def jira(since: str | None) -> None:
    """Fetch Jira tickets and sprints as JSON."""
    project_dir = find_project_dir()
    config = load_project(project_dir)
    run_sync_jira(config, since=since)


@sync.command()
@click.option("--since", default=None, help="Fetch messages since this date (YYYY-MM-DD). Omit for all messages.")
def slack(since: str | None) -> None:
    """Fetch Slack channel messages as JSON."""
    project_dir = find_project_dir()
    config = load_project(project_dir)
    run_sync_slack(config, since=since)


@sync.command()
def confluence() -> None:
    """Fetch Confluence pages as JSON."""
    project_dir = find_project_dir()
    config = load_project(project_dir)
    run_sync_confluence(config)
