from typing import IO

import click
from loguru import logger

from bin_tools.dataclasses.binset import BinSet
from bin_tools.export.binset_exporter import BinSetExporter


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
    help="Output file for trimmed bins (defaults to stdout)",
)
@click.argument(
    "binfile",
    type=click.File("rb"),
    nargs=1,
    required=True,
)
def trim(
    binfile: IO,
    output: IO,
    compress: bool = False,
):
    """Trim a BINS file by removing unreferenced contigs.

    BINFILE: Path to the BINS file to trim
    """
    try:
        logger.info(f"Reading binfile from {binfile.name}...")
        binset = BinSet.read_binfile(binfile)

        logger.info("Trimming unreferenced contigs...")
        trimmed_binset = binset.remove_unreferenced_contigs()

        logger.info("Writing trimmed binfile...")
        BinSetExporter(trimmed_binset).write_binfile(output, compress=compress)
        logger.info("Trim operation completed successfully.")

    except OSError as e:
        logger.error(f"File I/O error: {e}")
        raise click.ClickException(f"File I/O error: {e}")
