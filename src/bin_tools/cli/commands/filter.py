from typing import IO

import click
from loguru import logger

from bin_tools.dataclasses.binset import BinSet
from bin_tools.filter import filter_binset
from bin_tools.filter.query_parser import get_available_fields


@click.command("filter")
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
    help="(optional) Output file. Defaults to stdout.",
)
@click.option(
    "--list-fields",
    is_flag=True,
    help="List all available fields for filtering and exit.",
)
@click.argument("binfile", type=click.File("rb"), required=False)
@click.argument("query", required=False)
def filter_cmd(
    binfile: IO | None,
    query: str | None,
    output: IO,
    compress: bool = False,
    list_fields: bool = False,
):
    """Filter bins from a binfile based on a query expression.

    BINFILE: Input binfile to filter
    QUERY: Filter query (e.g., 'group == "group1" and completeness >= 0.9')

    Examples:
        # Filter by group
        bintools filter input.bin 'group == "high_quality"' -o output.bin

        # Filter by completeness and contamination
        bintools filter input.bin 'completeness >= 0.9 and contamination <= 0.05' -o output.bin

        # Filter by taxonomy
        bintools filter input.bin 'phylum == "Bacteroidetes"' -o output.bin

        # Combine multiple conditions
        bintools filter input.bin 'group == "archaea" and completeness >= 0.8' -o output.bin
    """
    if list_fields:
        click.echo("Available fields for filtering:")
        for field, description in sorted(get_available_fields().items()):
            click.echo(f"  {field:20} - {description}")
        return

    if binfile is None:
        logger.error("BINFILE argument is required (unless using --list-fields)")
        raise click.ClickException(
            "BINFILE argument is required (unless using --list-fields)"
        )

    if query is None:
        logger.error("QUERY argument is required (unless using --list-fields)")
        raise click.ClickException(
            "QUERY argument is required (unless using --list-fields)"
        )

    binset = BinSet.read_binfile(binfile)

    if binset.bins is None:
        logger.warning("No bins found in input file.")
        binset.write_binfile(output, compress=compress)
        return

    logger.info(f"Filtering {len(binset.bins)} bins with query: {query}")

    try:
        filtered_binset = filter_binset(binset, query)
    except ValueError as e:
        raise click.ClickException(f"Invalid filter query: {e}")

    logger.info(
        f"Filter complete: {len(filtered_binset.bins) if filtered_binset.bins else 0} "
        f"of {len(binset.bins)} bins matched."
    )

    filtered_binset.write_binfile(output, compress=compress)
