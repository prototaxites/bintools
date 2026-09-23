import sys

import click
from loguru import logger

from bin_tools.cli.commands.export import export_group
from bin_tools.cli.commands.import_data import import_group
from bin_tools.cli.commands.merge import merge
from bin_tools.cli.commands.rename import rename_bins
from bin_tools.cli.commands.summarise import summarise_group
from bin_tools.cli.commands.trim import trim
from bin_tools.cli.commands.view import view_bins


@click.group(context_settings={"max_content_width": 200})
def cli():
    logger.remove()
    logger.add(
        sys.stderr,
        format="[{time:HH:mm:ss}] | bintools | {level} - {message}",
        level="INFO",
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
