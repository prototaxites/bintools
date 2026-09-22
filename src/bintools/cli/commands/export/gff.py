from pathlib import Path
from typing import IO

import click
from loguru import logger

from bintools.dataclasses.binset import BinSet


@click.command("gff")
@click.option(
    "--outdir",
    "-o",
    type=click.Path(dir_okay=True, file_okay=False),
    required=True,
    default=".",
)
@click.option(
    "-g",
    "--group-gff",
    is_flag=True,
    help="(optional) Write each FASTA in a subdirectory named after the bin's group.",
)
@click.argument("binfile", type=click.File("rb"), nargs=1, required=True, default="-")
def gff(
    binfile: IO,
    outdir: str,
    group_gff: bool = False,
):
    """Write stored bin annotations to a set of GFF files.

    BINFILE: Path to the binfile to write GFFs for.
    """
    logger.info(f"Writing bins from {binfile.name}.")
    binset = BinSet.read(binfile)

    if not Path(outdir).exists():
        Path(outdir).mkdir(parents=True, exist_ok=True)

    binset.export_gff(
        outdir=Path(outdir),
        group_gff=group_gff,
    )
