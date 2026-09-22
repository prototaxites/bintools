from typing import IO

import click
from loguru import logger

from bin_tools.dataclasses.binset import BinSet


@click.command("trim")
@click.option(
    "--compress",
    "-z",
    "compress",
    is_flag=True,
    help="(optional) Compress the output using zstd.",
)
@click.option("--output", "-o", type=click.File("wb"), default="-", required=False)
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

    binset = BinSet.read_binfile(binfile)
    logger.info(f"Trimming contigs from {binfile.name}")
    trimmed_binset = binset.trim()
    trimmed_binset.write_binfile(output, compress=compress)
