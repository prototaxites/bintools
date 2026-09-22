import sys
from pathlib import Path
from typing import IO

import click
from loguru import logger

from bin_tools.dataclasses.binset import BinSet
from bin_tools.import_data.annotation import annotate_contigs


@click.command("annotation")
@click.option(
    "--compress",
    "-z",
    "compress",
    is_flag=True,
    help="(optional) Compress the output using zstd.",
)
@click.option(
    "--overwrite",
    type=bool,
    help="Overwrite existing annotations if they exist.",
    required=False,
)
@click.option("--output", "-o", type=click.File("wb"), default="-", required=False)
@click.argument("binfile", type=click.File("rb"), required=True, default="-")
@click.argument(
    "gff",
    type=click.Path(exists=True, dir_okay=False, file_okay=True),
    help="The GFF file to add the annotations from.",
    required=True,
)
def import_annotation(
    binfile: IO, gff: str, output: IO, compress: bool = False, overwrite: bool = False
):
    """Add annotations from a GFF file to a BINS file

    BINFILE: a BINS file to add the bins to.
    """
    binset = BinSet.read_binfile(binfile)

    logger.info("Annotating contigs.")
    try:
        annotated_contigs = annotate_contigs(
            binset.contigs,
            Path(gff),
            overwrite=overwrite,
        )
    except (ValueError, KeyError) as e:
        raise click.ClickException(f"Error: {e}")
    logger.info(f"Annotated {len(annotated_contigs)} contigs")

    binset.contigs = annotated_contigs
    binset.write_binfile(output, compress=compress)
