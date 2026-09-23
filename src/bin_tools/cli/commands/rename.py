from typing import IO

import click
from loguru import logger

from bin_tools.dataclasses.binset import BinSet
from bin_tools.export.binset_exporter import BinSetExporter
from bin_tools.query.query_parser import get_available_fields


@click.command("trim")
@click.option(
    "--compress",
    "-z",
    "compress",
    is_flag=True,
    help="(optional) Compress the output using zstd.",
)
@click.option(
    "--output",
    "-o",
    type=click.File("wb"),
    default="-",
    required=False,
    help="Output file for renamed bins (defaults to stdout)",
)
@click.option(
    "--bin-name",
    "-n",
    type=str,
    default=None,
    required=True,
    help="Name to assign to the bin group. Can include fields from the bin object itself, e.g. 'bin_{taxon}'. Always appends a _{n} count to avoid collisions. The list of fields can be viewed with --list-fields.",
)
@click.option(
    "--list-fields",
    is_flag=True,
    help="List all available fields for filtering and exit.",
)
@click.argument(
    "binfile",
    type=click.File("rb"),
    nargs=1,
    required=True,
)
def rename_bins(
    binfile: IO,
    output: IO,
    bin_name: str,
    list_fields: bool = False,
    compress: bool = False,
):
    """Rename bins in a BINS file.

    BINFILE: Path to the BINS file to rename bins in.
    """
    try:
        if list_fields:
            click.echo("Available fields for filtering:")
            for field, description in sorted(get_available_fields().items()):
                click.echo(f"  {field:20} - {description}")
            return

        logger.info(f"Reading binfile from {binfile.name}...")
        binset = BinSet.read_binfile(binfile)

        logger.info(f"Renaming bins with template: {bin_name}")
        trimmed_binset = binset.rename_bins(bin_name)

        logger.info("Writing renamed binfile...")
        BinSetExporter(trimmed_binset).write_binfile(output, compress=compress)
        logger.info("Rename operation completed successfully.")

    except OSError as e:
        logger.error(f"File I/O error: {e}")
        raise click.ClickException(f"File I/O error: {e}")
    except ValueError as e:
        logger.error(f"Invalid rename template: {e}")
        raise click.ClickException(f"Invalid rename template: {e}")
