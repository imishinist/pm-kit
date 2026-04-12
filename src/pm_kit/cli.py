import click

from pm_kit import __version__
from pm_kit.create import create
from pm_kit.sync.cli import sync


@click.group()
@click.version_option(version=__version__, prog_name="pm-kit")
def main():
    """pm-kit: AI-driven project management framework."""
    pass


main.add_command(create)
main.add_command(sync)
