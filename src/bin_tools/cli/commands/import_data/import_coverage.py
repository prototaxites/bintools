from pathlib import Path
from typing import IO

import click
from loguru import logger

from bin_tools.dataclasses.binset import BinSet
from bin_tools.enums import CoverageTool
from bin_tools.import_data.coverage import add_coverage


@click.command("coverage")
@click.option(
    "--compress",
    "-z",
    "compress",
    is_flag=True,
    help="(optional) Compress the output using zstd.",
)
@click.option(
    "--tool",
    type=click.Choice(CoverageTool),
    help="Tool used to estimate coverage.",
    required=False,
)
@click.option("--output", "-o", type=click.File("wb"), default="-", required=False)
@click.argument("binfile", type=click.File("rb"), required=True, default="-")
@click.argument(
    "coverage",
    type=click.Path(exists=True, dir_okay=False, file_okay=True),
    help="The GFF file to add the annotations from.",
    required=True,
)
def import_coverage(
    binfile: IO,
    coverage: str,
    output: IO,
    tool: CoverageTool,
    compress: bool = False,
):
    """Add annotations from a GFF file to a BINS file

    BINFILE: a BINS file to add the bins to.
    """
    binset = BinSet.read_binfile(binfile)

    logger.info("Adding coverage to contigs.")
    annotated_contigs = add_coverage(binset.contigs, Path(coverage), tool)
    logger.info(f"Annotated {len(annotated_contigs)} contigs")

    binset.contigs = annotated_contigs
    binset.write_binfile(output, compress=compress)
