from pathlib import Path
from typing import IO

import click
from loguru import logger

from bintools.dataclasses.binset import BinSet


@click.command("fasta")
@click.option(
    "--compress",
    "-z",
    "compress",
    is_flag=True,
    help="(optional) Compress the output using zstd.",
)
@click.option(
    "--outdir",
    "-o",
    type=click.Path(dir_okay=True, file_okay=False),
    required=True,
    default=".",
)
@click.option(
    "--preserve-headers",
    "-h",
    is_flag=True,
    help="(optional) Preserve headers in the output FASTA file.",
)
@click.option(
    "--group-fasta",
    "-g",
    is_flag=True,
    help="(optional) Write each FASTA in a subdirectory named after the bin's group.",
)
@click.argument("binfile", type=click.File("rb"), nargs=1, required=True, default="-")
def fasta(
    binfile: IO,
    outdir: str,
    compress: bool = False,
    preserve_headers: bool = False,
    group_fasta: bool = False,
):
    """Export a BINS file to FASTA.

    BINFILE: Path to the binfile to export FASTA for.
    """
    logger.info(f"Writing bins from {binfile.name}.")
    binset = BinSet.read(binfile)

    if not Path(outdir).exists():
        Path(outdir).mkdir(parents=True, exist_ok=True)

    binset.export_fasta(
        outdir=Path(outdir),
        compress=compress,
        preserve_headers=preserve_headers,
        group_fasta=group_fasta,
    )
