import click

from pm_kit import __version__
from pm_kit.adapter.cli import adapter
from pm_kit.create import create
from pm_kit.daily import daily
from pm_kit.overview import overview
from pm_kit.sync.cli import sync
from pm_kit.update import update


@click.group()
@click.version_option(version=__version__, prog_name="pm-kit")
def main():
    """pm-kit: AI-driven project management framework."""
    pass


main.add_command(adapter)
main.add_command(create)
main.add_command(daily)
main.add_command(overview)
main.add_command(sync)
main.add_command(update)
