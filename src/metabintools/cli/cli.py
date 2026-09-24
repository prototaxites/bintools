import sys

import click
from loguru import logger

from metabintools.cli.commands.export import export_group
from metabintools.cli.commands.import_data import import_group
from metabintools.cli.commands.merge import merge
from metabintools.cli.commands.rename import rename_bins
from metabintools.cli.commands.summarise import summarise_group
from metabintools.cli.commands.trim import trim
from metabintools.cli.commands.view import view_bins


@click.group(context_settings={"max_content_width": 200})
@click.version_option()
@click.option(
    "--log-level",
    default="INFO",
    help="Set the log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)",
)
def cli(log_level):
    logger.remove()
    logger.add(
        sys.stderr,
        format="[{time:HH:mm:ss}] | metabintools | {level} - {message}",
        level=log_level,
    )


cli.add_command(import_group, name="import")
cli.add_command(export_group, name="export")
cli.add_command(summarise_group, name="summarise")
cli.add_command(view_bins, name="view")
cli.add_command(merge, name="merge")
cli.add_command(trim, name="trim")
cli.add_command(rename_bins, name="rename")

if __name__ == "__main__":
    cli()
