import click

from pm_kit import __version__
from pm_kit.adapter.cli import adapter
from pm_kit.create import create
from pm_kit.schema import schema
from pm_kit.story_map.cli import story_map
from pm_kit.sync.cli import sync
from pm_kit.update import update


@click.group()
@click.version_option(version=__version__, prog_name="pm-kit")
def main():
    """pm-kit: AI-driven project management framework."""
    pass


main.add_command(adapter)
main.add_command(create)
main.add_command(schema)
main.add_command(story_map)
main.add_command(sync)
main.add_command(update)
