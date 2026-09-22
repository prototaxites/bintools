import sys

import click
from loguru import logger

from bin_tools.cli.commands.export import export_group
from bin_tools.cli.commands.filter import filter_cmd
from bin_tools.cli.commands.import_data import import_group
from bin_tools.cli.commands.merge import merge


@click.group()
def cli():
    logger.remove()
    logger.add(
        sys.stderr,
        format="[{time:HH:mm:ss}] | bintools | {level} - {message}",
        level="INFO",
    )


cli.add_command(import_group, name="import")
cli.add_command(export_group, name="export")
cli.add_command(filter_cmd, name="filter")
cli.add_command(merge, name="merge")

if __name__ == "__main__":
    cli()
