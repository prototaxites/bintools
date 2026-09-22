from pathlib import Path
from typing import IO

import click
from loguru import logger

from bintools.dataclasses.binset import BinSet


@click.command("contig2bin")
@click.option(
    "--output",
    "-o",
    type=click.Path(dir_okay=False, file_okay=True, exists=False),
    required=True,
    default=".",
)
@click.option(
    "-g",
    "--group",
    type=str,
    help="Write bins from a specific group.",
)
@click.argument("binfile", type=click.File("rb"), nargs=1, required=True, default="-")
def contig2bin(
    binfile: IO,
    output: str,
    group: str | None = None,
):
    """Write stored bin annotations to a set of GFF files.

    BINFILE: Path to the binfile to write GFFs for.
    """
    logger.info(f"Writing contig2bin file from {binfile.name}.")
    binset = BinSet.read(binfile)

    binset.export_contig2bin(
        path=Path(output),
        group=group,
    )
