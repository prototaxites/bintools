from typing import IO

import click
from loguru import logger

from bin_tools.dataclasses.binset import BinSet
from bin_tools.export.binset_exporter import BinSetExporter
from bin_tools.operations.merge import merge_binsets


@click.command("merge")
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
    help="Output file for merged binfiles (defaults to stdout)",
)
@click.argument(
    "binfiles",
    type=click.File("rb"),
    nargs=-1,
    required=True,
    help="Input binfiles to merge",
)
def merge(
    binfiles: list[IO],
    output: IO,
    compress: bool = False,
):
    """Merge a set of binfiles together.

    BINFILES: List of binfiles to merge
    """
    try:
        logger.info(f"Reading {len(binfiles)} binfile(s)...")
        binsets = []
        for i, binfile in enumerate(binfiles, 1):
            logger.info(f"Reading binfile {i}/{len(binfiles)}: {binfile.name}")
            binsets.append(BinSet.read_binfile(binfile))

        logger.info(f"Merging {len(binfiles)} binfiles...")
        merged = merge_binsets(binsets)

        logger.info("Writing merged binfile...")
        BinSetExporter(merged).write_binfile(output, compress=compress)
        logger.info("Merge operation completed successfully.")

    except click.ClickException:
        raise
    except OSError as e:
        logger.error(f"File I/O error: {e}")
        raise click.ClickException(f"File I/O error: {e}")
