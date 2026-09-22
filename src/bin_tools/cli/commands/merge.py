from typing import IO

import click
from loguru import logger

from bin_tools.dataclasses.binset import BinSet
from bin_tools.merge.merge import merge_binsets


@click.command("merge")
@click.option(
    "--compress",
    "-z",
    "compress",
    is_flag=True,
    help="(optional) Compress the output using zstd.",
)
@click.option("--output", "-o", type=click.File("wb"), default="-", required=False)
@click.argument(
    "binfiles",
    type=click.File("rb"),
    nargs=-1,
    required=True,
)
def merge(
    binfiles: list[IO],
    output: IO,
    compress: bool = False,
):
    """Merge a set of binfiles together.

    BINFILES: List of binfiles to merge
    """
    binsets = [BinSet.read_binfile(binfile) for binfile in binfiles]
    logger.info(f"Merged {len(binfiles)} binfiles.")

    merged = merge_binsets(binsets)
    merged.write_binfile(output, compress=compress)
