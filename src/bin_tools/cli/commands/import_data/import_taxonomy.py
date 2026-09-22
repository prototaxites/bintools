from pathlib import Path
from typing import IO

import click
from loguru import logger

from bin_tools.dataclasses.binset import BinSet
from bin_tools.enums import TaxonomyTool
from bin_tools.import_data.taxonomy import add_taxonomy


@click.command("taxonomy")
@click.option(
    "--compress",
    "-z",
    "compress",
    is_flag=True,
    help="(optional) Compress the output using zstd.",
)
@click.option(
    "--tool",
    type=click.Choice(TaxonomyTool),
    help="The tool used to assign taxonomy to the bins.",
    required=True,
    default=TaxonomyTool.MANUAL,
)
@click.option(
    "--taxonomy",
    type=click.Path(exists=True, dir_okay=False, file_okay=True),
    help="Input file containing taxonomy information.",
    required=True,
)
@click.option("--output", "-o", type=click.File("wb"), default="-", required=False)
@click.argument("binfile", type=click.File("rb"), required=True, default="-")
def import_taxonomy(
    binfile: IO,
    output: IO,
    taxonomy: str,
    tool: TaxonomyTool,
    compress: bool = False,
):
    """Add a set of quality scores to a BINS file.

    BINFILE: a BINS file to add the bins to
    """
    binset = BinSet.read_binfile(binfile)
    if binset.bins is None:
        logger.error("No bins found in the BINS file.")
        raise click.ClickException("No bins found in the BINS file.")

    updated_bins = add_taxonomy(binset.bins, Path(taxonomy), tool)
    out_binset = binset.model_copy(update={"bins": updated_bins})
    out_binset.write_binfile(output, compress=compress)
